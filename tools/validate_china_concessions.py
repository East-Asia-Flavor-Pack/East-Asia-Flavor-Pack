"""Static integration checks for China's concessions (not an engine interpreter).

Run: python tools/validate_china_concessions.py --game-root "C:/Users/user/Documents/GitHub/Vic3-vanilla" --source-only
Omit --source-only when checking an installed game with its assets.
Runtime scenarios and limitations are in scratch/china_concessions_design_plan.md.
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
    parser.add_argument("--source-only", action="store_true",
                        help="Skip asset existence checks for a vanilla script checkout")
    args = parser.parse_args()
    game = args.game_root
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
                 "weekly_income", "eafp_concession_host_debit",
                 "eafp_concession_state_debit", "eafp_concession_holder_credit")
    for key in forbidden:
        assert not re.search(r"\b" + key + r"\b", clean), ("Removed mechanism", key)
    assert not re.search(r"\b(?:set_global_variable|change_variable|create_obligation|remove_obligation)\s*=", clean)
    # Only an unreconstructable historical loss is stored. No ownership/cap ledger.
    variable_writes = re.findall(r"\bset_variable\s*=\s*\{\s*name\s*=\s*(\w+)", clean)
    assert variable_writes and set(variable_writes) == {"concession_loss_prestige_snapshot"}
    assert len(variable_writes) == len(re.findall(r"\bset_variable\s*=", clean))
    assert "remove_variable = concession_loss_prestige_snapshot" in clean

    hooks = read(ROOT / "common/on_actions/concessions_code_on_actions.txt")
    entries = read(ROOT / "common/on_actions/00_code_on_actions_definition.txt")
    effects = read(ROOT / "common/scripted_effects/eafp_concessions_effects.txt")
    treaties = read(ROOT / "common/treaty_articles/eafp_concessions_treaty_articles.txt")
    je = read(ROOT / "common/journal_entries/eafp_concessions_in_china.txt")
    je_code = unquoted(je)
    assert re.findall(r"^(je_\w+)\s*=", je_code, re.M) == ["je_concessions_in_china"]
    assert definitions["je_concessions_in_china2"] == 0, "No country-specific concession JE"
    assert "group = je_group_global_international_situations" in je_code
    groups_code = unquoted("\n".join(read(p) for p in (game / "common/journal_entry_groups").glob("*.txt")))
    assert re.search(r"je_group_global_international_situations\s*=\s*\{\s*context\s*=\s*none", groups_code)
    assert re.search(r"should_show_when_not_involved\s*=\s*\{\s*always\s*=\s*yes\s*\}", je_code)
    # Visibility does not activate a contextless journal; possible is the auto-start gate.
    assert not re.search(r"\bpossible\s*=", je_code), \
        "The international JE must activate through the treaty, not automatically"
    entry_force = unquoted(treaties).split("on_entry_into_force = {", 1)[1].split("on_enforced", 1)[0]
    assert -1 < entry_force.find("eafp_concession_grant_effect = yes") \
        < entry_force.find("add_contextless_journal_entry = je_concessions_in_china"), \
        "Treaty entry into force must activate the international JE after granting rights"
    assert len(re.findall(r"\badd_contextless_journal_entry\s*=", clean)) == 1
    assert not re.search(r"\b(?:outcome|complete|fail|invalid|timeout|transferable|\w+_all_involved)\s*=", je_code), \
        "The international JE must persist and calculate only once per pulse"
    assert len(re.findall(r"\bon_weekly_pulse\s*=", je_code)) == 1
    assert len(re.findall(r"\bon_monthly_pulse\s*=", je_code)) == 1
    assert re.search(r"on_weekly_pulse\s*=\s*\{\s*effect\s*=\s*\{\s*eafp_concession_refresh_effect\s*=\s*yes", je_code)
    assert re.search(r"on_monthly_pulse\s*=\s*\{\s*effect\s*=\s*\{\s*every_state\s*=", je_code)
    assert "should_be_involved = { eafp_concession_involved_country = yes }" in je_code
    assert "add_involved_country = prev" in je_code and "remove_involved_country = prev" in je_code
    for obsolete in ("eafp_concessions_start", "eafp_concessions_weekly", "eafp_concessions_monthly"):
        assert not re.search(r"\b" + obsolete + r"\b", clean + unquoted(entries)), ("Obsolete timer", obsolete)
    assert not re.search(r"\badd_journal_entry\s*=", clean), "Use contextless international JE activation"
    assert "can_be_renegotiated" not in unquoted(treaties)
    assert len(re.findall(r"on_enforced\s*=\s*\{\s*\}", treaties)) == 1
    assert definitions["eafp_return_concession"] == 0, "Return is handled by treaty withdrawal"
    assert "eafp_return_concession" not in clean, "Removed return article must not be referenced"
    assert re.search(r"on_withdrawal\s*=\s*\{\s*scope:article\s*=", treaties)
    assert len(re.findall(r"eafp_concession_return_effect\s*=\s*\{\s*FORCED\s*=\s*(?:yes|no)\s*\}", treaties)) == 2
    assert "scope:article.treaty.remaining_binding_period > 0" in treaties
    assert "scope:withdrawing_country = scope:concession_host" in treaties
    assert not re.search(r"eafp_concession_return_effect\s*=\s*yes", scripts)
    assert re.search(r"on_break\s*=\s*\{\s*\}", treaties), "Break already runs withdrawal cleanup"

    # Withdrawal rule must match vanilla treaty_port exactly (whitespace-insensitive).
    def can_withdraw_block(text):
        body = unquoted(text).split("can_withdraw = {", 1)[1]
        depth, end = 1, 0
        for end, char in enumerate(body):
            depth += {"{": 1, "}": -1}.get(char, 0)
            if not depth:
                break
        return " ".join(body[:end].split())
    assert can_withdraw_block(treaties) == can_withdraw_block(
        read(game / "common/treaty_articles/14_treaty_port.txt")), "can_withdraw differs from vanilla treaty_port"
    assert "source_modifier" not in treaties and "target_modifier" not in treaties
    assert effects.count("add_treasury") == 1, "Only paid expansion charges the treasury"
    # The weekly Chinese-treasury-to-holder transfer and its modifiers are removed entirely.
    assert not re.search(r"\bconcession_pa(?:yment|id)\b", clean), \
        "No recurring treasury transfer from the Chinese owner to holders"
    assert "EAFP_CONCESSION_AI_INCOME" not in treaties, "Treaty AI must not value a removed transfer"
    assert "building_trade_center" not in unquoted(effects), "No vanilla trade center reward or deletion"
    # Grant and paid expansion both move in steps of 5 levels.
    assert effects.count("eafp_concession_add_company_level = { LEVELS = 5 }") == 2
    assert "LEVELS = 1 }" not in effects
    assert effects.count("levels = $LEVELS$") == 2
    grant_gate = read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt").split("eafp_concession_can_grant = {", 1)[1].split("eafp_concession_has_holder = {", 1)[0]
    assert "eafp_concession_free_capacity >= 5" in grant_gate
    assert "add_company = company_type:company_eafp_concession" in effects
    assert "remove_company = company_type:company_eafp_concession" in effects
    assert "NOT = { eafp_concession_holder_has_rights = yes }" in effects
    assert "eafp_concession_expand_effect = yes" in je_code
    assert "eafp_concession_expand_effect = yes" in read(ROOT / "common/scripted_guis/concessions_in_china_sgui.txt")
    assert "eafp_concession_free_capacity >= 1" not in read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt")
    assert not re.search(r"\blevel\s*=", unquoted(effects)), "Use additive ownership, not a fixed level"
    assert "eafp_concession_grant_effect" not in hooks, "Inheritance must not award buildings"
    values = read(ROOT / "common/script_values/eafp_concessions_values.txt")
    assert values.count("add = weekly_profit") == 1
    assert re.search(r"eafp_concession_urban_cap\s*=\s*\{\s*value = eafp_concession_urban_levels\s*multiply = 5\s*\}", values)
    assert re.search(r"eafp_concession_trade_equivalent\s*=\s*\{\s*value = eafp_concession_total_levels\s*\}", values)
    # Verify the live shared-building definitions against installed vanilla.
    building = read(ROOT / "common/buildings/eafp_concessions_buildings.txt")
    assert re.findall(r"^(building_eafp_concession\w*)\s*=", building, re.M) == ["building_eafp_concession"]
    for setting in ("buildable", "expandable", "downsizeable"):
        assert re.search(r"\b" + setting + r"\s*=\s*no", building)
    # The dedicated building group was removed (9edd39e3); the building uses vanilla bg_trade.
    assert re.search(r"\bbuilding_group\s*=\s*bg_trade\b", building)
    # Every PM the scripts activate must belong to one of the building's PM groups
    # (mod base group + vanilla trade-quantity group). Balance numbers are the author's.
    pm_groups = {}
    for path in [*(ROOT / "common/production_method_groups").glob("*.txt"),
                 *(game / "common/production_method_groups").glob("*.txt")]:
        for name, body in re.findall(r"(?m)^(pmg_\w+)\s*=\s*\{(.*?)^\}", unquoted(read(path)), re.S):
            block = re.search(r"production_methods\s*=\s*\{([^}]*)\}", body)
            pm_groups.setdefault(name, re.findall(r"\w+", block[1]) if block else [])
    building_pmgs = re.findall(r"\bpmg_\w+", building.split("production_method_groups", 1)[1].split("}", 1)[0])
    allowed_pms = {pm for group in building_pmgs for pm in pm_groups[group]}
    used_pms = set(re.findall(r"\bpm_\w+", "\n".join(re.findall(r"activate_production_methods?\s*=\s*\{[^}]*\}", unquoted(effects)))))
    used_pms |= set(re.findall(r"has_active_production_method\s*=\s*(pm_\w+)", unquoted(effects)))
    assert used_pms and used_pms <= allowed_pms, ("PM outside the building's groups", used_pms - allowed_pms)
    # Only the return and the rightless-state refresh remove the building.
    assert re.findall(r"remove_building\s*=\s*(\w+)", unquoted(effects + je)) == ["building_eafp_concession"] * 2
    # Increase = overwrite the holder's ownership on the live building (user design 2026-11-11).
    rebuild = effects.split("eafp_concession_add_company_level = {", 1)[1].split("\n}", 1)[0]
    assert "remove_building" not in unquoted(rebuild), "Expansion must not remove the building"
    assert "flag:cash_reserve" not in effects and "cash_reserves_ratio" not in effects
    assert "clear_variable_map = eafp_concession_rebuild_map" in rebuild
    assert "eafp_concession_rebuild_map_add = { KEY = scope:concession_holder VALUE = scope:eafp_rebuild_added }" in rebuild
    assert rebuild.index("eafp_concession_measure_country_levels = { COUNTRY = scope:concession_holder }") \
        < rebuild.index("eafp_concession_rebuild_owner_levels = yes"), "Read the holder's levels, then overwrite"
    assert effects.count("eafp_concession_measure_country_levels = { COUNTRY =") == 2
    # Grant and expansion judge success by the holder's expected total, not a total-level rise.
    assert effects.count("value >= scope:concession_expected_levels") == 3
    assert "concession_previous_levels" not in effects
    # create_building levels do not stack on an existing building: one call per owner,
    # dispatched to the 5-level step that matches the stored value.
    assert "eafp_concession_rebuild_chunk" not in rebuild and "eafp_concession_rebuild_owner_levels = yes" in rebuild
    assert "while" not in effects.split("eafp_concession_rebuild_chunk = {", 1)[1].split("\n}", 1)[0]
    dispatch = effects.split("eafp_concession_rebuild_owner_levels = {", 1)[1].split("\n}", 1)[0]
    steps = [int(x) for x in re.findall(r"eafp_concession_rebuild_chunk = \{ LEVELS = (\d+) \}", dispatch)]
    cases = [int(x) for x in re.findall(r"^\t\t(\d+) = \{", dispatch, re.M)]
    assert re.search(r"switch = \{\s*trigger = scope:eafp_rebuild_remaining\s", dispatch), "Dispatch with switch"
    assert "if =" not in dispatch and "else" not in dispatch
    assert steps == list(range(5, steps[-1] + 1, 5)) and steps[-1] >= 250, steps[-3:]
    assert cases == steps, "Each switch case n runs the chunk with LEVELS = n"
    assert "custom_tooltip = {\n\t\t\ttext = eafp_concession_expand_effect_tt\n\t\t\teafp_concession_expand_effect = yes" \
        in read(ROOT / "common/scripted_guis/concessions_in_china_sgui.txt").replace("\r\n", "\n")
    assert "NOT = { any_in_list = { variable = concession_owner_varlist always = yes } }" in effects
    assert re.search(r"else_if\s*=\s*\{\s*limit\s*=\s*\{\s*has_building\s*=\s*building_eafp_concession\s*\}\s*remove_building\s*=\s*building_eafp_concession\s*\}", effects)
    refresh = effects[effects.index("eafp_concession_refresh_effect = {"):]
    assert "eafp_concession_urban_cap" not in refresh and "eafp_concession_over_capacity" not in refresh
    assert "levels = -" not in effects, "Do not assume unsupported negative ownership removal"
    assert "count = 32" in effects and "value >= scope:concession_level_mid" in effects
    assert "level_after_queued_constructions = level" in je_code, "Include waiting construction in duplicate prevention"
    queue_types = re.findall(r"start_privately_funded_building_construction\s*=\s*(\w+)", je_code)
    assert queue_types and len(queue_types) == len(set(queue_types))
    vanilla_buildings = "\n".join(read(p) for p in (game / "common/buildings").glob("*.txt"))
    for key in queue_types:
        assert re.search(r"^" + key + r"\s*=", vanilla_buildings, re.M), key
        assert "can_construct_building = " + key in je_code, key
    assert "eafp_concession_free_capacity >= 1" not in read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt")
    assert b"## weekly_profit" in (ROOT / "documentation/triggers.log").read_bytes()
    mods = read(ROOT / "common/static_modifiers/eafp_chi_modifiers.txt")
    assert not re.search(r"^concession_pa(?:yment|id)\s*=", mods, re.M), "Transfer modifiers are removed"

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
    assert actual_groups <= groups.keys(), ("Unknown building groups", actual_groups - groups.keys())

    def selected_by_filter(key):
        # is_building_group includes descendants, as in vanilla's manufacturing decree.
        while key:
            if key in actual_groups:
                return True
            key = groups[key].get("parent_group")
        return False

    covered_groups = {key for key in groups if selected_by_filter(key)}
    assert covered_groups == expected_groups, ("Urban filter mismatch", covered_groups ^ expected_groups)
    region = "geographic_region_china_proper"
    assert definitions[region] == 1, ("Missing/duplicate concession region", region)
    assert set(re.findall(r"is_in_geographic_region\s*=\s*(\w+)", clean)) == {region}, \
        "Concession geography must use China Proper"
    assert re.search(r"eafp_concession_eligible_state\s*=\s*\{\s*"
                     r"is_in_geographic_region\s*=\s*" + region + r"\b", gates)
    if not args.source_only:
        for asset in set(re.findall(r'(?:icon|texture|video)\s*=\s*"?([^"\s{}]+)', code)):
            assert (ROOT / asset).is_file() or (game / asset).is_file(), ("Missing asset", asset)

    gui = read(ROOT / "gui/journal_entry_widgets/eafp_concessions_in_china.gui")
    assert 'name = "widget_eafp_concessions"' in gui
    assert je.count('name = "widget_eafp_concessions"') == 1
    sgui = read(ROOT / "common/scripted_guis/concessions_in_china_sgui.txt")
    assert "JournalEntry.GetCountry" not in gui and "viewer" not in gui + sgui, \
        "All observers must see the same international overview"
    assert "scripted_button" not in je
    # The international widget reads live state and ownership; its accordion is UI-only.
    assert "State.GetIDString" in gui and "GetVariableSystem.SetOrToggle" in gui
    assert "IsDataModelEmpty(GetGlobalList('concession_candidate_states_gvarlist'))" in gui
    assert "BuildingOwnership.IsCountryOwned" in gui
    for key in re.findall(r"GetScriptedGui\('([^']+)'\)", gui):
        assert key in definitions, ("Missing GUI action", key)
    for key in re.findall(r"ScriptValue\('([^']+)'\)", gui):
        assert key in definitions, ("Missing GUI value", key)
    assert "eafp_concession_cap_usage" in values
    # Catch divide-by-zero and overflow regressions in the visual meter.
    cap_usage = values.split("eafp_concession_cap_usage = {", 1)[1]
    assert "divide = { value = eafp_concession_urban_cap min = 1 }" in cap_usage
    assert "max = 1" in cap_usage
    keys = set(re.findall(r"(?:text|tooltip|title|desc|flavor|name|custom_tooltip)\s*=\s*\"?((?:concessions_in_china\.\d+\.|eafp_(?:grant|return)_concession_|eafp_concession_|EAFP_CONCESSION_AI_)\w+)", code))
    # Script names, effects, and saved scopes are not localization keys.
    keys = {k for k in keys if k not in definitions
            and k not in ("eafp_concession_compensation", "eafp_concession_rebuild_map")}
    for key in ("je_concessions_in_china",):
        keys.update((key, key + "_reason"))
    for key in ("eafp_grant_concession",):
        # The article's _desc text was removed on purpose (2026-11-11); no code references it.
        keys.update(key + suffix for suffix in ("", "_effects_desc", "_article_short_desc"))
    keys.update(("concept_concession_desc",
                 "eafp_concession_active_label", "eafp_concession_inactive_label"))
    keys.update(key for key in feature_definitions
                if key.startswith(("building_eafp_", "bg_eafp_", "company_eafp_", "pm_eafp_", "pmg_eafp_")))
    keys.update(("eafp_concession_company_slot", "eafp_concession_forced_loss", "eafp_concession_right_live", "eafp_concession_right_returned"))
    keys.update("war_goal_eafp_concession_incident_return" + s
                for s in ("", "_type_name", "_type_desc", "_desc", "_sway_desc"))
    keys.update("dp_eafp_concession_incident" + s for s in ("", "_desc", "_tooltip"))
    # SelectLocalization branches are not direct text= keys.
    keys.update("eafp_concession_" + suffix for suffix in (
        "cap_available", "cap_full", "cap_exceeded",
        "company_ownership_row", "company_right_tt"))
    localizations = {}
    for lang in LANGUAGES:
        catalog = {}
        for path in (ROOT / "localization" / lang).glob("*.yml"):
            for key, value in re.findall(r'^\s*([\w.]+):(?:\d+)?\s*"((?:\\.|[^"\\])*)"\s*$', read(path), re.M):
                catalog.setdefault(key, []).append(value)
        path = ROOT / "localization" / lang / f"eafp_china_l_{lang}.yml"
        structural_check(path)
        assert read(path).splitlines()[0] == "l_" + lang + ":"
        for key in keys:
            assert len(catalog.get(key, [])) == 1, ("Missing/duplicate localization", lang, key)
        assert "BuildingOwnership.GetOwnershipRatio" in catalog["eafp_concession_asset_amount"][0]
        localized_gui = gui + "\n" + "\n".join(catalog[k][0] for k in keys)
        for pattern in (r"GetScriptedGui\('([^']+)'\)", r"ScriptValue\('([^']+)'\)"):
            for key in re.findall(pattern, localized_gui):
                assert key in definitions, ("Missing localized UI reference", lang, key)
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
          "international journal pulses, hooks, treaty callbacks, removed mechanisms and encoding.")
    print("SKIP: asset existence (--source-only)." if args.source_only else "PASS: asset existence.")
    print("PASS: shared building, one-to-one trade-center PMs, initial five levels, five-times urban cap, queue duplicate prevention and industry references.")
    print("Game execution skipped: company lifecycle, private queue attribution and GUI are not runtime-verified. "
          "Known limitations: owner-specific shared-level removal and partial production suspension are unavailable.")


if __name__ == "__main__":
    main()

