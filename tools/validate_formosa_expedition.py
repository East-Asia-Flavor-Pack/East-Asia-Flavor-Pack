"""Check Formosa progression boundaries and localization from the actual scripts.

Run: python tools/validate_formosa_expedition.py
The small trigger evaluator covers this chain only, not engine scope/UI behavior.
"""
from pathlib import Path
import operator
import re

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def block(text, key):
    start = re.search(r'(?m)^\s*' + re.escape(key) + r'\s*=\s*\{', text)
    assert start, key
    depth = 1
    for end in range(start.end(), len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if depth == 0:
            return text[start.end():end]
    raise AssertionError(f"Unclosed block: {key}")


def parse(text):
    tokens = iter(re.findall(r'"[^"\n]*"|>=|<=|[{}=<>]|[^\s{}=<>]+', text))

    def entries():
        result = []
        for key in tokens:
            if key == "}":
                return result
            op, value = next(tokens), next(tokens)
            result.append((key.strip('"'), op, entries() if value == "{" else value))
        return result

    return entries()


def allows(nodes, progress=0, variables=frozenset(), claim=False, active=True, surveying=False):
    def check(key, op, value):
        if key == "text":
            return True
        if isinstance(value, list):
            result = allows(value, progress, variables, claim, active, surveying)
            return not result if key == "NOT" else result
        if key == "has_variable":
            return value in variables
        if key == "has_claim":
            return claim
        if key == "has_journal_entry":
            return active
        if key == "has_modifier":
            return surveying
        if key.startswith("scripted_bar_progress("):
            return {">=": operator.ge, ">": operator.gt, "=": operator.eq}[op](progress, int(value))
        raise AssertionError(f"Unsupported trigger: {key}")

    return all(check(*node) for node in nodes)


def main():
    journal = block(read("common/journal_entries/eafp_japan.txt"), "je_formosa_expedition")
    buttons = read("common/scripted_buttons/eafp_japan_buttons.txt")
    events = read("events/eafp_jap_events/eafp_formosa_expedition_events.txt")
    bar = read("common/scripted_progress_bars/eafp_formosa_expedition_progress_bars.txt")
    pulse = block(block(journal, "on_weekly_pulse"), "effect")
    claim_gate = parse(block(pulse, "limit"))
    maximum = int(re.search(r"max_value\s*=\s*(\d+)", bar)[1])

    # The claim requires only a completed survey, including saves without activity flags.
    for progress in (0, 6, 12, 18, maximum - 1, maximum):
        assert allows(claim_gate, progress) == (progress == maximum)
    assert not allows(claim_gate, maximum, claim=True)
    assert not allows(claim_gate, maximum, {"eafp_formosa_claim_event_sent"})
    assert "set_variable = eafp_formosa_claim_event_sent" in pulse
    assert "add_claim" not in journal
    assert events.count("add_claim = ROOT") == 1

    # Starting and pausing are available only in their respective survey states.
    start_button = block(buttons, "start_formosa_survey_button")
    assert re.findall(r"scripted_button\s*=\s*(\w+)", journal) == ["start_formosa_survey_button", "pause_formosa_survey_button"]
    for condition in ("visible", "possible"):
        gate = parse(block(start_button, condition))
        assert allows(gate)
        assert not allows(gate, surveying=True)
        assert not allows(gate, claim=True)
    assert block(start_button, "effect").strip() == "add_modifier = formosa_survey_modifier"
    assert set(re.findall(r"(?m)^formosa_expedition_events\.(\d+)\s*=", events)) == {"1", "2"}

    pause_button = block(buttons, "pause_formosa_survey_button")
    for condition in ("visible", "possible"):
        gate = parse(block(pause_button, condition))
        assert allows(gate, surveying=True)
        assert not allows(gate, surveying=False)
        assert not allows(gate, surveying=True, claim=True)
    # Removing only the modifier preserves all accumulated progress for resumption.
    assert block(pause_button, "effect").strip() == "remove_modifier = formosa_survey_modifier"

    # Progress requires an active survey; claim and ownership both stop its upkeep.
    monthly_gate = parse(block(block(bar, "monthly_progress"), "limit"))
    assert allows(monthly_gate, surveying=True)
    assert not allows(monthly_gate, surveying=False)
    assert not allows(monthly_gate, surveying=True, claim=True)
    assert "remove_modifier = formosa_survey_modifier" in block(journal, "on_complete")
    assert "remove_modifier = formosa_survey_modifier" in block(block(events, "formosa_expedition_events.2"), "option")
    assert "owns_entire_state_region = STATE_FORMOSA" in block(journal, "complete")

    # All displayed text references must exist exactly once in each supported language.
    feature_text = "\n".join([journal, bar, events, start_button, pause_button])
    refs = set(re.findall(r'\b(?:name|desc|title|flavor|text|custom_tooltip)\s*=\s*"?((?:je_formosa|formosa_|eafp_formosa_|modifier_formosa|start_formosa|pause_formosa)[\w.]*)', feature_text))
    refs |= {"je_formosa_expedition", "je_formosa_expedition_reason", "je_formosa_expedition_goal", "formosa_survey_modifier"}
    for language in ("korean", "english", "simp_chinese"):
        path = ROOT / f"localization/{language}/eafp_japan_l_{language}.yml"
        assert path.read_bytes().startswith(b"\xef\xbb\xbf"), path
        text = path.read_text(encoding="utf-8-sig")
        keys = re.findall(r'^\s*([\w.]+):(?:\d+)?\s*"', text, re.M)
        for ref in refs:
            assert keys.count(ref) == 1, (language, ref)
        assert "formosa_scope" not in text

    print("Formosa checks passed: survey boundaries, start/pause flow, duplicate guards, cleanup, and 3-language references.")


if __name__ == "__main__":
    main()
