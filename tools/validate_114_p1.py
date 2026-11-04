"""Source-level P1 integration checks against the 1.14_beta vanilla checkout.

Run: python -B tools/validate_114_p1.py --game-root /path/to/Vic3-vanilla
Does not simulate AI weights, engine scopes, inheritance hooks or naval battles.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block
from validate_114_p0 import body, code, read
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]
GOAL = "eafp_restore_military_headquarters_china"
LANGUAGES = ("korean", "english", "simp_chinese")


def definitions(root, folder):
    result = {}
    for path in (root / "common" / folder).glob("*.txt"):
        text = path.read_text(encoding="utf-8-sig")
        for key in re.findall(r"(?m)^(?:REPLACE:|INJECT:)?(\w+)\s*=\s*\{", text):
            result[key] = path
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    game = parser.parse_args().game_root
    vanilla = lambda path: (game / path).read_text(encoding="utf-8-sig")
    compact = lambda text: re.sub(r"\s+", "", code(text))

    decision = body(read("common/decisions/eafp_00_korea_decisions.txt"), "KOR_declare_korean_empire")
    possible = body(decision, "possible")
    assert "is_independent_and_not_being_subjugated = yes" in possible
    assert "has_variable = eafp_var_sam_all_clear" in possible
    donghak = body(read("common/journal_entries/eafp_03_korea.txt"), "je_donghak_movement")
    for gate in ("is_shown_in_lobby", "is_shown_when_inactive"):
        assert "is_in_geographic_region = geographic_region_korea" in body(donghak, gate)
    north = read("common/journal_entries/eafp_07_taming_the_north.txt")
    assert compact(body(north, "fail")) == "NOT={has_or_is_contesting_state_in_state_region=STATE_HOKKAIDO}"
    assert "add_journal_entry = { type = je_karafuto }" in body(north, "on_complete")

    # Both admission and the random selection must exclude countries at war with Japan.
    incident = body(read("events/000_eafp_japan_overrides.txt"), "ep2_meiji_pulse.1")
    port = body(body(incident, "trigger"), "any_state_in_home_islands")
    selected = body(body(body(incident, "immediate"), "random_state_in_home_islands"), "limit")
    neighbour = body(selected, "any_neighbouring_state")
    for candidate in (port, neighbour):
        assert "is_treaty_port = yes" in candidate
        assert compact(body(candidate, "owner")) == "NOT={has_war_with=root}"
    assert "owner = ROOT" in selected
    assert "owner = ROOT" in body(port, "any_neighbouring_state")
    for gate, selector in (("trigger", "any_in_global_list"), ("immediate", "random_in_global_list")):
        assert "NOT = { has_war_with = root }" in body(body(incident, gate), selector)
    assert "save_scope_as = japan_scope" in incident and "save_scope_as = namamugi_daimyo_state" in incident

    opium = read("common/journal_entries/eafp_00_opium_wars.txt")
    assert body(opium, "complete").strip().startswith("NOT = { has_war_with = scope:target }")
    reunify = body(read("common/journal_entries/eafp_00_reunify_china.txt"), "je_reunify_china")
    assert "is_at_war = no" in body(reunify, "invalid")
    assert not re.search(r"(?m)^\s*complete\s*=", reunify)
    assert "clear_variable_list = chi_war_dynamism_varlist" in body(reunify, "on_invalid")
    plays = read("common/diplomatic_plays/eafp_diplomatic_plays.txt")
    for key in ("dp_taiping_rebellion", "dp_unify_china"):
        assert "ai_acceptance_max = 75" in body(plays, key)
    assert "always = no" in code(body(body(plays, "dp_taiping_rebellion"), "additional_involvement_trigger"))
    unify_gate = code(body(body(plays, "dp_unify_china"), "possible"))
    assert unify_gate.count("has_journal_entry = je_reunify_china") == 2
    assert "has_global_variable = china_shatters" in unify_gate
    assert "global_var:chinese_central_government ?= THIS" in unify_gate
    pair = body(vanilla("common/scripted_triggers/00_diplomacy_triggers.txt"), "is_china_unification_pair")
    assert "has_journal_entry = je_reunify_china" in body(pair, "OR")
    assert "has_journal_entry = je_reunify_china" in body(pair, "$TARGET$")

    # Restoring a liberated headquarters must create the same subject type, not a tributary.
    subject = read("common/subject_types/eafp_military_headquarters.txt")
    assert "forced_into_overlord_revolution = yes" in subject
    assert f"re_establish_war_goal = {GOAL}" in subject
    goal_path = "common/war_goal_types/eafp_subject_war_goals.txt"
    goal = body(read(goal_path), GOAL)
    reference = body(vanilla("common/war_goal_types/34_make_personal_union.txt"), "make_personal_union")
    expected = reference.replace("subject_type_personal_union", "subject_type_military_headquarters_china")
    expected = expected.replace("make_dominion.dds", "make_tributary.dds")
    assert compact(goal) == compact(expected), "Restoration must retain vanilla make_subject validation/mirror/infamy rules"
    assert compact(body(goal, "possible")) == "always=no", "Restoration-only goal must not permit manual subjugation"
    action = read("common/diplomatic_actions/eafp_subject_military_headquarters_china.txt")
    assert "subject_type = subject_type_military_headquarters_china" in body(action, "pact")
    tokens = {}
    for language in LANGUAGES:
        path = f"localization/{language}/eafp_china_l_{language}.yml"
        structural_check(ROOT / path)
        catalog = "\n".join(p.read_text(encoding="utf-8-sig") for p in (ROOT / "localization" / language).glob("*.yml"))
        tokens[language] = {}
        for suffix in ("", "_type_name", "_type_desc", "_desc", "_sway_desc"):
            key = "war_goal_" + GOAL + suffix
            values = re.findall(r'^\s*' + key + r':\d*\s*"([^\n]*)"', catalog, re.M)
            assert len(values) == 1, (language, key)
            tokens[language][key] = Counter(re.findall(r"\[[^\]]+\]|\$[^$]+\$", values[0]))
    assert tokens["korean"] == tokens["english"] == tokens["simp_chinese"]

    # These vanilla changes are inherited; adding duplicate on-actions or effects would be a regression.
    effects = definitions(ROOT, "scripted_effects")
    for key in ("on_new_ruler_japan_effect", "transition_off_of_monarchy_effects"):
        assert key not in effects
        assert key in definitions(game, "scripted_effects")
    hooks = read("common/on_actions/00_code_on_actions_definition.txt")
    assert "on_new_ruler_japan_effect" not in hooks and "on_treaty_ports_inherited" not in hooks
    assert "on_new_ruler_japan_effect = yes" in vanilla("common/on_actions/00_code_on_actions.txt")
    templates = definitions(ROOT, "character_templates")
    stock_templates = vanilla("common/character_templates/country_jap.txt")
    for name in ("kokaku", "ninko", "komei", "meiji", "taisho", "showa", "moriko", "sumiko", "chikako"):
        key = f"JAP_{name}_yamato"
        assert key not in templates
        assert "culture = cu:japanese" in body(stock_templates, key)
    movements = read("common/political_movements/zz_eafp_ideological_movements.txt")
    for key in ("movement_meiji_restorationist", "movement_tokugawa_loyalist"):
        assert body(movements, key).count('desc = "movement_suppressed_after_civil_war"') == 1
    parties = read("common/parties/eafp_parties.txt")
    names = re.findall(r"(?m)^INJECT:(\w+)\s*=", parties)
    assert len(names) == 11
    stock_parties = definitions(game, "parties")
    for key in names:
        patch = body(parties, "INJECT:" + key)
        assert key in stock_parties
        start, end, _ = find_block(patch, "name")
        remainder = code(patch[:start] + patch[end:]).strip()
        if remainder:
            assert key in ("military_party", "radical_party")
            assert compact(remainder) == compact(find_block(remainder, "color")[2]), key

    # AI extensions and naval-industry references must still resolve in the new data set.
    base_ai = body(vanilla("common/ai_strategies/00_default_strategy.txt"), "ai_strategy_default")
    for key in ("diplomatic_play_support", "aggression", "recklessness", "diplomatic_play_boldness",
                "wargoal_maneuvers_fraction", "state_value", "wargoal_scores"):
        find_block(base_ai, key)
    ref_files = [*sorted((ROOT / "common/ai_strategies").glob("*.txt")),
                 ROOT / "events/eafp_kor_events/eafp_korean_reformation_events.txt",
                 ROOT / "events/eafp_chi_events/eafp_chinese_westernization_events.txt",
                 ROOT / "common/journal_entries/eafp_korean_reformation.txt"]
    texts = "\n".join(code(p.read_text(encoding="utf-8-sig")) for p in ref_files)
    for prefix, folder in (("building_", "buildings"), ("bg_", "building_groups"), ("pm_", "production_methods")):
        known = definitions(game, folder) | definitions(ROOT, folder)
        refs = set(re.findall(r"\b" + prefix + r"[a-z_]+\b", texts))
        # Strategy field names share the building_ prefix but are not object references.
        refs -= {"building_group_weights", "building_scope"}
        assert refs <= known.keys(), (folder, sorted(refs - known.keys()))
    assert "ship_group_weights" not in texts

    for path in (
        "common/decisions/eafp_00_korea_decisions.txt", "common/journal_entries/eafp_03_korea.txt",
        "common/journal_entries/eafp_07_taming_the_north.txt", "common/journal_entries/eafp_00_opium_wars.txt",
        "common/journal_entries/eafp_00_reunify_china.txt", "common/diplomatic_plays/eafp_diplomatic_plays.txt",
        "common/subject_types/eafp_military_headquarters.txt", "common/scripted_effects/eafp_japan_effects.txt",
        "events/000_eafp_japan_overrides.txt", "events/heavenly_kingdom_events.txt", goal_path,
    ):
        structural_check(ROOT / path)
    print("PASS: P1 eligibility/selection and peace guards, unification constraints, headquarters restoration;")
    print("      5 goal keys in 3 languages, inherited Japanese succession/9 cultures, 11 party names, movement suppression;")
    print("      7 AI extension fields, regional-AI/shipbuilding references, BOM/CRLF and delimiters.")
    print("Game execution, AI balance, occupation/peace lifecycle and naval performance remain runtime checks.")


if __name__ == "__main__":
    main()
