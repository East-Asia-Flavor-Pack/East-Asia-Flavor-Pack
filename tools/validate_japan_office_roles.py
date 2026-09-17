"""Validate the integration of Japan's three scripted offices (not an engine test).

Run with: python -B tools/validate_japan_office_roles.py
"""
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]
POSITIONS = ("roju", "rojushuza", "tairo")


def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def block(text, key):
    definition = re.search(rf"(?m)^(?:REPLACE:)?{re.escape(key)}\s*=\s*\{{", text)
    if definition:
        text = text[definition.start():]
    return find_block(text, key)[2]


def clean(text):
    return re.sub(r"#[^\n]*", "", text)


def main():
    paths = [
        "common/character_roles/eafp_japan_character_roles.txt",
        "common/scripted_triggers/eafp_jap_triggers.txt",
        "common/scripted_effects/eafp_japan_effects.txt",
        "common/character_templates/eafp_character_templates_JAP.txt",
        "common/history/global/eafp_global.txt",
        "common/on_actions/eafp_japan_regional_on_actions.txt",
        "common/journal_entries/eafp_japan.txt",
        "events/eafp_jap_events/eafp_japan.txt",
    ]
    for lang in ("korean", "english", "simp_chinese"):
        paths.append(f"localization/{lang}/eafp_japan_character_roles_l_{lang}.yml")
    for path in paths:
        structural_check(ROOT / path)

    roles, triggers, effects = (read(p) for p in paths[:3])
    all_roles = "\n".join(p.read_text(encoding="utf-8-sig")
                          for p in (ROOT / "common/character_roles").glob("*.txt"))
    assert "REPLACE:character_role_politician" not in all_roles
    public = block(triggers, "is_bakufu_politician")
    career = block(effects, "set_bakufu_politician_career_length")
    for pos in POSITIONS:
        role = f"character_role_eafp_{pos}"
        assert len(re.findall(rf"(?m)^{role}\s*=", all_roles)) == 1
        definition = block(roles, role)
        assert "type = politician" in definition
        assert "auto_assigned = no" in definition
        assert "spawn_characters_to_pool = no" in definition
        assert "character_modifier" not in definition
        callback = block(definition, "on_career_end")
        assert f"POSITION = flag:{pos}" in callback
        assert "eafp_japan_on_bakufu_office_career_end" in callback
        assert "has_role" not in callback  # Expired role may already be absent.
        assert f"has_role = {role}" in block(triggers, f"is_{pos}")
        assert f"has_role = {role}" in public
        assert f"role = {role}" in career
        for lang in ("korean", "english", "simp_chinese"):
            loc = read(f"localization/{lang}/eafp_japan_character_roles_l_{lang}.yml")
            assert loc.startswith(f"l_{lang}:")
            assert len(re.findall(rf'^ {role}:\s*".+"$', loc, re.M)) == 1
    assert "role = character_role_politician" not in career
    assert "add_career_length" not in career

    # Startup coverage must match the historical office and remaining time.
    history = read(paths[4])
    incumbents = [
        ("JAP_ii_naoaki", "tairo", 60, (1.0, 1.2), (60, 72)),
        ("eafp_jap_okubo_tadazane_template", "rojushuza", 12, (1, 2), (12, 24)),
        ("eafp_jap_matsudaira_norihiro_template", "roju", 24, (1.5, 2), (36, 48)),
        ("JAP_tadakuni_mizuno", "roju", 48, (1.75, 2), (84, 96)),
        ("eafp_jap_matsudaira_muneakira_template", "roju", 48, (1, 1.25), (48, 60)),
        ("eafp_jap_ota_sukemoto_template", "roju", 60, (1, 1.2), (60, 72)),
    ]
    for template, pos, months, span, expected in incumbents:
        tail = history.split(f"template = {template}", 1)[1]
        start = block(tail, "on_created")
        assert f"eafp_japan_assign_bakufu_office = {{ POSITION = flag:{pos} }}" in start
        assert start.index("eafp_japan_assign_bakufu_office") < start.index("set_career_length")
        timer = block(start, "set_career_length")
        assert f"role = character_role_eafp_{pos}" in timer
        actual_months = int(re.search(r"months = (\d+)", timer)[1])
        actual_span = tuple(map(float, re.search(r"random_range = \{ ([\d.]+) ([\d.]+) \}", timer).groups()))
        assert (actual_months, actual_span) == (months, span)
        assert tuple(months * x for x in span) == expected

    events = read(paths[7])
    promotion = block(events, "eafp_japan.5")
    assert promotion.count("eafp_japan_assign_bakufu_office = { POSITION = flag:rojushuza }") == 5
    assert promotion.count("set_bakufu_politician_career_length = yes") == 1
    assert promotion.index("set_bakufu_politician_career_length") > promotion.rindex("eafp_japan_assign_bakufu_office")
    # Cache registration belongs only to the assignment helper, never a caller.
    registration = block(effects, "eafp_japan_assign_bakufu_office_unchecked")
    pattern = r"(?:set_variable|add_to_variable_list)\s*=\s*\{\s*name\s*=\s*(?:tairo_var|rojushuza_var|roju_varlist)\b"
    assert len(re.findall(pattern, registration)) == 3
    assert not re.search(pattern, effects.replace(registration, ""))
    assert not re.search(pattern, history + events)

    end = block(effects, "eafp_japan_end_bakufu_office")
    assert "var:eafp_bakufu_office_position ?= $POSITION$" in end
    for guard in ("eafp_bakufu_office_transition", "eafp_bakufu_office_ending"):
        assert f"NOT = {{ has_variable = {guard} }}" in end
    assert "appoint_roju_effect" not in end and "appoint_rojushuza_effect" not in end
    death = block(read(paths[5]), "eafp_japan_on_bakufu_politician_death")
    assert "has_variable = eafp_bakufu_office_position" in death
    assert "remove_bakufu_politician_role" in death
    save = block(effects, "save_bakufu_politician_mission")
    assert "var:eafp_bakufu_office_position ?= flag:roju" in save
    assert "var:eafp_bakufu_office_position ?= flag:rojushuza" in save
    assert "remove_character_role = politician" not in effects

    journal = block(read(paths[6]), "je_bakuhantaisei")
    for key in ("on_complete", "on_invalid"):
        part = block(journal, key)
        assert "remove_bakufu_politician_role_without_appointment" in part
        assert "set_variable = eafp_bakufu_offices_dissolving" in part
    weekly = block(journal, "on_weekly_pulse")
    assert "set_career_length" not in weekly and "set_bakufu_politician_career_length" not in weekly
    assert "eafp_japan_assign_bakufu_office" not in weekly  # No save migration/role recreation.
    assert "id = eafp_japan.9" not in journal + history

    templates = read(paths[3])
    assert "role = character_role_magnate" not in block(templates, "eafp_jap_matsudaira_muneakira_template")
    assert "role = character_role_magnate" in block(templates, "JAP_ii_naoaki")
    assert "eafp_japan_is_ii_daimyo" not in triggers + effects
    assert "eafp_house_ii" not in triggers + effects
    assert not (ROOT / "common/scripted_effects/eafp_japan_ii_house_effects.txt").exists()
    recruitment = block(effects, "create_bakufu_politician_character")
    candidate = block(recruitment, "random_scope_character")
    assert "has_role_of_type = magnate" in candidate
    assert "var:daimyo_var ?= s:STATE_KYOTO" in candidate
    assert "set_last_name = Ii" not in recruitment
    assert "set_last_name = Sakai" in recruitment
    assert "name = daimyo_var" not in recruitment and "character_role_magnate" not in recruitment
    assert "switch =" not in block(recruitment, "while")
    print("PASS: office roles, 6 initial tenures, 5 promotion branches, guarded lifecycle, cache ownership, Ii eligibility, 3 localizations, BOM/CRLF.")


if __name__ == "__main__":
    main()
