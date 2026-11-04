"""Targeted source checks for the Victoria 3 1.14 P0 migration.

Run: python -B tools/validate_114_p0.py
Evaluates reward boundaries from scripts and UI expressions; does not simulate
the engine's scopes, INJECT merging, occupation timers or peace settlements.
"""
import ast
import operator
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block
from validate_formosa_expedition import parse
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]
VAR = "eafp_var_jqw_current_war_support"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def code(text):
    return re.sub(r"#[^\n]*", "", text)


def body(text, key):
    block = find_block(text, key)[2]
    return block[block.index("{") + 1:block.rindex("}")]


def blocks(text, key):
    result = []
    while re.search(r"(?m)^\s*" + re.escape(key) + r"\s*=\s*\{", text):
        _, end, block = find_block(text, key)
        result.append(block[block.index("{") + 1:block.rindex("}")])
        text = text[end:]
    return result


def allows(nodes, support):
    def check(key, op, value):
        if key == "has_variable":
            assert value == VAR
            return support is not None
        if key == f"var:{VAR}":
            return {">=": operator.ge, "<": operator.lt}[op](support or 0, float(value))
        if key in ("AND", "OR", "NOT"):
            checks = [check(*node) for node in value]
            return any(checks) if key == "OR" else not all(checks) if key == "NOT" else all(checks)
        raise AssertionError(f"Unsupported reward trigger: {key}")
    return all(check(*node) for node in nodes)


def ui_checks(line, support):
    expressions = re.findall(r"\[(SelectLocalization\([^\]]+\))\]", line)
    assert len(expressions) == 3
    variable = f"SCOPE.GetRootScope.GetCountry.MakeScope.Var('{VAR}')"
    functions = {
        "And": lambda a, b: a and b, "Or": lambda a, b: a or b,
        "Not": operator.not_, "GreaterThanOrEqualTo_CFixedPoint": operator.ge,
        "LessThan_CFixedPoint": operator.lt,
        "SelectLocalization": lambda condition, yes, no: yes if condition else no,
    }
    result = []
    for expression in expressions:
        expression = expression.replace(variable + ".IsSet", str(support is not None))
        expression = expression.replace(variable + ".GetValue", str(support or 0))
        expression = re.sub(r"'\(CFixedPoint\)(\d+)'", r"\1", expression)
        tree = ast.parse(expression, mode="eval")
        # Only these known pure UI functions and literal arguments may execute.
        assert all(isinstance(n, (ast.Expression, ast.Call, ast.Name, ast.Load, ast.Constant))
                   for n in ast.walk(tree))
        assert all(n.id in functions for n in ast.walk(tree) if isinstance(n, ast.Name))
        result.append(eval(compile(tree, "<reward UI>", "eval"), {"__builtins__": {}}, functions)
                      == "@green_checkmark_box!")
    return result


def main():
    triggers = read("common/scripted_triggers/eafp_kor_triggers.txt")
    tiers = ("high", "medium", "low")
    gates = [parse(body(triggers, f"eafp_jqw_war_support_{tier}_trigger")) for tier in tiers]
    below_high = parse(body(triggers, "eafp_jqw_war_support_below_high_trigger"))
    localizations = []
    for language in ("korean", "english", "simp_chinese"):
        path = ROOT / f"localization/{language}/eafp_joseon_qing_war_l_{language}.yml"
        structural_check(path)
        text = path.read_text(encoding="utf-8-sig")
        assert text.startswith(f"l_{language}:\n")
        localizations.append(next(line for line in text.splitlines()
                                  if line.lstrip().startswith("je_eafp_joseon_qing_war_progress:")))
    for support in (None, *range(101), 49.99, 74.99):
        expected = 1 if support is None else 0 if support >= 75 else 1 if support >= 50 else 2
        selected = [allows(gate, support) for gate in gates]
        assert sum(selected) == 1 and selected[expected], (support, selected)
        assert allows(below_high, support) == (expected != 0)
        for line in localizations:
            assert ui_checks(line, support) == selected, support

    journal = read("common/journal_entries/eafp_joseon_qing_war.txt")
    snapshot = f'value = "scope:joseon_qing_war.has_war_support(root)"'
    assert snapshot in body(journal, "immediate") and snapshot in body(journal, "on_weekly_pulse")
    assert journal.index("save_scope_as = joseon_qing_war") < journal.index(snapshot)
    for condition in ("complete", "fail"):
        assert "any_scope_war" in body(journal, condition)
    events = read("events/eafp_kor_events/eafp_joseon_qing_war_events.txt")
    options = blocks(body(events, "eafp_joseon_qing_war_events.2"), "option")
    assert len(options) == 3
    for tier, option in zip(tiers, options):
        assert f"eafp_jqw_war_support_{tier}_trigger = yes" in body(option, "trigger")
        assert f"eafp_jqw_victory_{tier}_reward_effect = yes" in option
        assert f"remove_variable = {VAR}" in option

    # Shared setup must not depend on the player's country selection.
    heavenly = code(body(read("events/heavenly_kingdom_events.txt"), "heavenly.4"))
    immediate = body(heavenly, "immediate")
    for call in ("assign_taiping_states = yes", "create_taiping_characters = yes",
                 "chi_chimeric_empire_decline = yes", "add_treasury = prev.var:gold_transfer_nil",
                 "add_treasury = var:gold_transfer", "type = je_hui_revolt_pre",
                 "type = je_taiping_pre", "type = je_taiping_revolution_pre"):
        assert immediate.count(call) == heavenly.count(call) == 1, call
    options = [parse(option) for option in blocks(heavenly, "option")]
    assert len(options) == 2
    assert {n[0] for n in options[0]} == {"name", "default_option", "ai_chance"}
    assert {n[0] for n in options[1]} == {"name", "ai_chance", "play_as"}
    assert "create_diplomatic_play" not in heavenly and "add_diplomatic_play_war_support" not in heavenly
    taiping = code(read("common/journal_entries/eafp_00_taiping.txt"))
    pre = body(taiping, "je_taiping_pre")
    assert "timeout = 60" in pre
    timeout = body(pre, "on_timeout")
    assert timeout.count("create_diplomatic_play") == timeout.count("add_diplomatic_play_war_support") == 1
    assert timeout.index("create_diplomatic_play") < timeout.index("add_diplomatic_play_war_support")
    bonus = body(timeout, "random_diplomatic_play")
    assert all(s in body(bonus, "limit") for s in (
        "initiator = c:TPG", "target = c:CHI", "is_diplomatic_play_type = dp_taiping_rebellion"))
    assert "target = c:TPG value = 50" in bonus
    assert "recently_had_war" not in taiping and "has_variable = recently_lost_war" in taiping

    # Mid-war occupation must not count again at the peace settlement.
    registration = code(read("common/on_actions/00_code_on_actions_definition.txt"))
    assert registration.count("eafp_on_wargoal_enforced") == 1
    assert "eafp_on_wargoal_enforced" in body(registration, "on_wargoal_enforced")
    assert "on_wargoal_enforced_by_timer" not in registration
    hook = code(body(read("common/on_actions/eafp_code_on_actions.txt"), "eafp_on_wargoal_enforced"))
    assert "temp_wargoal_impact" not in hook and not re.search(r"\bowner\s*=", hook)
    for scope, sign in (("target", 1), ("actor", -1)):
        scopes = blocks(hook, f"scope:{scope} ?")
        assert len(scopes) == 2 and "has_journal_entry = je_eastasian_expansionism" in scopes[0]
        progress = body(scopes[1], "add_progress")
        assert "value = scope:wargoal_impact" in progress
        assert ("multiply = -1" in progress) == (sign == -1)
    opium = read("common/journal_entries/eafp_first_opium_war.txt")
    for key, target in (("je_first_opium_war", "scope:target"), ("je_qing_first_opium_war", "c:GBR")):
        for condition in ("complete", "fail"):
            gate = code(body(body(opium, key), condition)).strip()
            assert gate.startswith(f"NOT = {{ has_war_with = {target} }}")
    treaty = code(read("common/treaty_articles/eafp_concessions_treaty_articles.txt"))
    assert "eafp_concession_grant_effect = yes" in body(treaty, "on_entry_into_force")
    assert "eafp_concession_return_effect = yes" in body(treaty, "on_withdrawal")
    assert not body(treaty, "on_enforced").strip() and not body(treaty, "on_break").strip()
    goal = code(read("common/war_goal_types/eafp_concessions_war_goals.txt"))
    assert "mirrored_wargoal" not in goal and "eafp_concession_return_effect = yes" in body(goal, "on_enforced")

    # No live references to the retired APIs may remain.
    for directory in ("common", "events"):
        for path in (ROOT / directory).rglob("*.txt"):
            assert not re.search(r"\b(?:country_war_exhaustion_casualties_mult|has_war_exhaustion)\b",
                                 code(path.read_text(encoding="utf-8-sig"))), path
    modifiers = read("common/static_modifiers/eafp_chi_modifiers.txt")
    assert "country_war_support_casualties_mult = 0.25" in body(modifiers, "INJECT:taiping_taiping_rebellion")
    assert "country_war_support_casualties_mult = -0.9" in body(modifiers, "xinhai_revolution_army_modifier")
    arrow = body(read("common/decisions/eafp_arrow_incident_decision.txt"), "has_war_support")
    ezo = body(body(read("events/000_eafp_japan_overrides.txt"), "ezo_republic.2"), "has_war_support")
    assert "target = c:CHI" in arrow and "value < 50" in arrow and "value < 50" in ezo
    scripts = (
        "common/decisions/eafp_arrow_incident_decision.txt", "common/static_modifiers/eafp_chi_modifiers.txt",
        "common/scripted_triggers/eafp_kor_triggers.txt", "common/journal_entries/eafp_joseon_qing_war.txt",
        "common/journal_entries/eafp_00_taiping.txt", "common/journal_entries/eafp_first_opium_war.txt",
        "common/on_actions/eafp_code_on_actions.txt", "events/000_eafp_japan_overrides.txt",
        "events/heavenly_kingdom_events.txt",
    )
    for path in scripts:
        structural_check(ROOT / path)
    print("PASS: 104 support cases, exclusive rewards and 3-language UI parity; initial snapshot;")
    print("      shared Taiping setup and delayed bonus; final-only enforcement and peace gates;")
    print("      concession callback ownership; retired APIs; BOM/CRLF and script delimiters.")
    print("Engine execution and game balance remain runtime checks.")


if __name__ == "__main__":
    main()
