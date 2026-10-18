"""Static integration checks for China's concessions (not an engine interpreter).

Run: python tools/validate_china_concessions.py --game-root "D:/SteamLibrary/steamapps/common/Victoria 3/game"
Runtime scenarios and limitations are in documentation/china_concessions_design_plan.md.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("korean", "english", "simp_chinese")


def read(path):
    return path.read_text(encoding="utf-8-sig")


def unquoted(text):
    return re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*', "", text)


def feature_files():
    return sorted(p for folder in ("common", "events", "gui")
                  for p in (ROOT / folder).rglob("*")
                  if p.suffix in (".txt", ".gui") and "concession" in p.name)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    game = parser.parse_args().game_root
    assert (game / "common/treaty_articles/treaty_articles.md").is_file(), game

    files = feature_files()
    assert files, "No active concession scripts"
    for file in files + [ROOT / "common/on_actions/00_code_on_actions_definition.txt",
                         ROOT / "common/static_modifiers/eafp_chi_modifiers.txt"]:
        structural_check(file)
    code = "\n".join(read(p) for p in files)
    clean = unquoted(code)
    definitions = Counter()
    for folder in ("common", "events"):
        for path in (ROOT / folder).rglob("*.txt"):
            definitions.update(re.findall(r"^([\w.]+)\s*=\s*\{", unquoted(read(path)), re.M))
    scripts = unquoted("\n".join(read(p) for p in files if p.suffix == ".txt"))
    feature_definitions = set(re.findall(r"^([\w.]+)\s*=\s*\{", scripts, re.M))
    for key in feature_definitions:
        assert definitions[key] == 1, ("Duplicate definition", key, definitions[key])
    calls = set(re.findall(r"\b(eafp_concession\w+)\s*(?:=|[<>])", scripts))
    for key in calls:
        assert key in definitions, ("Missing scripted definition", key)

    forbidden = ("eafp_concession_revision", "eafp_concession_weekly_paid",
                 "eafp_concessions_schema_version", "concession_anchor",
                 "grant_bp", "max_region_bp", "capacity_per_urban_level_bp",
                 "base_monthly_per_urban_level", "fixed_monthly_cost",
                 "variable_cost_ratio", "disruption_factor", "representation_factor",
                 "works_extra_cost", "prestige_per_grant", "prestige_country_cap",
                 "weekly_income")
    for key in forbidden:
        assert not re.search(r"\b" + key + r"\b", clean), ("Removed mechanism", key)
    assert not re.search(r"\b(?:set_variable|set_global_variable|change_variable|create_obligation|remove_obligation)\s*=", clean)

    hooks = read(ROOT / "common/on_actions/concessions_code_on_actions.txt")
    entries = read(ROOT / "common/on_actions/00_code_on_actions_definition.txt")
    effects = read(ROOT / "common/scripted_effects/eafp_concessions_effects.txt")
    treaties = read(ROOT / "common/treaty_articles/eafp_concessions_treaty_articles.txt")
    assert len(re.findall(r"on_action\s*=\s*eafp_concessions_weekly\s+days\s*=\s*7", hooks)) == 2
    assert "on_action = eafp_concessions_weekly" not in effects
    assert entries.count("eafp_concessions_start") == 1
    assert entries.count("eafp_concessions_monthly") == 1
    assert "can_be_renegotiated" not in unquoted(treaties)
    assert len(re.findall(r"on_enforced\s*=\s*\{\s*\}", treaties)) == 2
    assert "source_modifier" not in treaties and "target_modifier" not in treaties
    assert "add_treasury" not in effects
    assert not re.search(r"\blevel\s*=", unquoted(effects)), "Use additive ownership, not a fixed level"
    assert "eafp_concession_grant_effect" not in hooks, "Inheritance must not award buildings"
    values = read(ROOT / "common/script_values/eafp_concessions_values.txt")
    assert values.count("add = weekly_profit") == 1
    assert b"## weekly_profit" in (ROOT / "documentation/triggers.log").read_bytes()
    mods = read(ROOT / "common/static_modifiers/eafp_chi_modifiers.txt")
    for key, sign in (("concession_payment", "-1"), ("concession_paid", "1")):
        assert re.search(r"^" + key + r"\s*=\s*\{[^}]*country_tax_income_add\s*=\s*" + sign + r"\s*\}", mods, re.M)

    # Check all installed urban building-group inheritance, including owner buildings.
    groups = {}
    paths = sorted((game / "common/building_groups").glob("*.txt"))
    paths += sorted((ROOT / "common/building_groups").glob("*.txt"))
    for path in paths:
        parts = re.split(r"(?m)^(bg_\w+)\s*=\s*\{", read(path))
        for i in range(1, len(parts), 2):
            group = groups.setdefault(parts[i], {})
            for attr in ("parent_group", "category"):
                match = re.search(r"(?m)^\s*" + attr + r"\s*=\s*(\w+)", parts[i + 1])
                if match:
                    group[attr] = match[1]

    def category(key, visited=()):
        assert key not in visited, ("Group inheritance cycle", key)
        group = groups[key]
        if "category" in group:
            return group["category"]
        parent = group.get("parent_group")
        return category(parent, visited + (key,)) if parent else None

    expected_groups = {key for key in groups if category(key) == "urban"}
    gates = read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt")
    actual_groups = set(re.findall(r"is_building_group\s*=\s*(bg_\w+)", gates))
    assert actual_groups == expected_groups, ("Urban filter mismatch", actual_groups ^ expected_groups)
    region = "geographic_region_han_homelands"
    assert any(re.search(r"^" + region + r"\s*=", read(p), re.M)
               for p in (game / "common/geographic_regions").glob("*.txt"))
    for asset in set(re.findall(r'(?:icon|texture|video)\s*=\s*"?([^"\s}]+)', code)):
        assert (ROOT / asset).is_file() or (game / asset).is_file(), ("Missing asset", asset)

    gui = read(ROOT / "gui/journal_entry_widgets/eafp_concessions_in_china.gui")
    je = read(ROOT / "common/journal_entries/eafp_concessions_in_china.txt")
    assert 'name = "widget_eafp_concessions"' in gui
    assert je.count('name = "widget_eafp_concessions"') == 2
    assert "scripted_button" not in je
    keys = set(re.findall(r"(?:text|tooltip|title|desc|flavor|name|custom_tooltip)\s*=\s*\"?((?:concessions_in_china\.\d+\.|eafp_(?:grant|return)_concession_|eafp_concession_|EAFP_CONCESSION_AI_)\w+)", code))
    # Script names, effects, and saved scopes are not localization keys.
    keys = {k for k in keys if k not in definitions and k != "eafp_concession_compensation"}
    for key in ("je_concessions_in_china", "je_concessions_in_china2"):
        keys.update((key, key + "_reason", key + "_status"))
    for key in ("eafp_grant_concession", "eafp_return_concession"):
        keys.update(key + suffix for suffix in ("", "_desc", "_effects_desc", "_article_short_desc"))
    keys.update(("concept_concession_desc", "concession_payment", "concession_paid",
                 "eafp_concession_active_label", "eafp_concession_inactive_label"))
    keys.update("war_goal_eafp_concession_incident_return" + s
                for s in ("", "_type_name", "_type_desc", "_desc", "_sway_desc"))
    keys.update("dp_eafp_concession_incident" + s for s in ("", "_desc", "_tooltip"))
    localizations = {}
    for lang in LANGUAGES:
        catalog = {}
        for path in (ROOT / "localization" / lang).glob("*.yml"):
            for key, value in re.findall(r'^\s*([\w.]+):(?:\d+)?\s*"((?:\\.|[^"\\])*)"\s*$', read(path), re.M):
                catalog.setdefault(key, []).append(value)
        for path in (ROOT / "localization" / lang).glob("eafp_concessions*.yml"):
            structural_check(path)
            assert read(path).splitlines()[0] == "l_" + lang + ":"
        for key in keys:
            assert len(catalog.get(key, [])) == 1, ("Missing/duplicate localization", lang, key)
        localizations[lang] = catalog

    for key in keys:
        tokens = []
        for lang in LANGUAGES:
            value = localizations[lang][key][0]
            tokens.append(Counter(re.findall(r"\[[^\]]+\]|\$[^$]+\$", value)))
        assert tokens[0] == tokens[1] == tokens[2], ("Translated tokens differ", key)
    events = re.findall(r"^concessions_in_china\.(\d+)\s*=", clean, re.M)
    assert len(events) == 8 and len(set(events)) == 8
    print(f"PASS: {len(files)} feature files; {len(feature_definitions)} unique definitions; "
          f"{len(expected_groups)} urban groups; {len(keys)} localized keys in 3 languages; "
          "assets, hooks, treaty callbacks, removed mechanisms and encoding.")
    print("Runtime behavior (money units, ownership +5, state selection, war goal targets, "
          "save/reload, state merge order and GUI) still requires Victoria 3.")


if __name__ == "__main__":
    main()

