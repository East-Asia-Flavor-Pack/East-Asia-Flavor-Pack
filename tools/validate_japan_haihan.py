"""Validate the handoff from Bakufu administration to abolition of the domains.

Run: python -B tools/validate_japan_haihan.py
Static integration checks; actual event and GUI execution requires Victoria 3.
"""
from pathlib import Path
import re

from validate_japan_office_roles import block
from validate_japan_regional_content import REGIONS, structural_check

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def main():
    paths = [
        "common/journal_entries/eafp_00_meiji_restoration.txt",
        "common/scripted_buttons/eafp_japan_haihan_button.txt",
        "common/scripted_triggers/eafp_japan_reform_triggers.txt",
        "common/scripted_triggers/eafp_japan_regional_triggers.txt",
        "common/scripted_effects/eafp_japan_regional_effects.txt",
        "common/scripted_effects/eafp_japan_effects.txt",
        "events/eafp_jap_events/eafp_haihan.txt",
        "events/000_eafp_japan_overrides.txt",
        "common/scripted_guis/eafp_japan_regions_sgui.txt",
        "gui/journal_entry_widgets/eafp_je_bakuhantaisei.gui",
    ]
    for path in paths:
        structural_check(ROOT / path)
    journal, button, reform, gates, regions, effects, event, overrides, sgui, gui = map(read, paths)

    # No circular requirement: petition first, abolition after the Emperor takes power.
    assert "eafp_japan_haihan_completed" not in block(reform, "eafp_japan_kogi_yoron_petition_ready")
    for key in ("eafp_japan_imperial_victory", "eafp_japan_kogi_yoron_conditions"):
        assert "eafp_japan_haihan_completed = yes" in block(reform, key)
    assert "has_global_variable = japan_daimyo_abolished" in block(reform, "eafp_japan_haihan_completed")
    restoration = block(journal, "je_meiji_restoration")
    assert "scripted_button = eafp_japan_haihan_button" in restoration
    assert "eafp_japan_haihan_completed = yes" in block(restoration, "on_monthly_pulse")
    assert "country_clear_daimyo" not in restoration
    assert "country_clear_daimyo" not in block(overrides, "meiji.1")
    possible = block(button, "possible")
    assert "NOT = { has_law = law_type:law_bakufu }" in possible
    assert "has_trait = special_character_japanese_emperor" in possible
    assert "is_not_in_civil_war = yes" in possible
    assert "eafp_japan_daimyo_list_active = yes" in block(button, "visible")
    assert "id = eafp_japan.5001" in button
    immediate = block(event, "immediate")
    assert immediate.index("country_clear_daimyo = yes") < immediate.index("eafp_japan_end_regions = yes")
    assert "je_meiji_restoration_update_daimyos = yes" in immediate
    assert "country_calculate_and_cache_daimyo_loyalties_per_state = yes" in immediate

    # Ending administration must preserve live rosters, but must never reactivate bars.
    active = block(gates, "eafp_japan_regional_active")
    assert "NOT = { has_variable = eafp_japan_regional_ended }" in active
    listing = block(gates, "eafp_japan_daimyo_list_active")
    assert "NOT = { has_global_variable = japan_daimyo_abolished }" in listing
    assert "has_journal_entry" not in listing and "has_law" not in listing
    end = block(regions, "eafp_japan_end_regions")
    assert end.index("set_variable = eafp_japan_regional_ended") < end.index("eafp_japan_refresh_regions = yes")
    assert "clear_variable_list" not in end and "remove_variable = eafp_japan_region_state_" not in end
    roster = block(regions, "eafp_japan_refresh_region_daimyos")
    assert roster.index("clear_variable_list") < roster.index("every_scope_character")
    assert "is_character_alive = yes" in roster and "has_variable = daimyo_var" in roster
    assert "eafp_japan_daimyo_list_active = yes" in roster
    assert "eafp_japan_regional_active" not in roster
    cache = block(effects, "country_calculate_and_cache_daimyo_loyalties_per_state")
    assert "eafp_japan_refresh_regions = yes" in block(cache, "else")
    assert "eafp_japan_daimyo_list_active = yes" in sgui
    assert "GetScriptedGui('eafp_japan_regions_visible').IsShown" in gui
    for region in REGIONS:
        assert f"GetList('eafp_japan_region_daimyos_{region}')" in gui
        assert f"Not(JournalEntry.GetCountry.MakeScope.Var('eafp_japan_region_active_{region}').IsSet)" not in gui
        assert re.search(r"visible = .*region_active_" + region + r".*\n\s*direction = vertical\n\s*spacing = 4\n\s*green_progressbar_horizontal", gui)

    # New button/event keys must be complete and unique in each language.
    keys = set(re.findall(r"(?:name|desc|title|flavor|text|custom_tooltip) = (eafp_japan(?:_haihan|\.5001)[\w.]*)", button + event + reform))
    assert len(keys) == 7
    for lang in ("korean", "english", "simp_chinese"):
        path = ROOT / f"localization/{lang}/eafp_japan_l_{lang}.yml"
        structural_check(path)
        text = path.read_text(encoding="utf-8-sig")
        for key in keys:
            assert len(re.findall(r"^" + re.escape(key) + r':\s*".+"$', text, re.M)) == 1, (lang, key)
    print("PASS: abolition button/event, both victory paths, petition reachability, persistent rosters, hidden bars, 3 localizations, BOM/CRLF.")


if __name__ == "__main__":
    main()
