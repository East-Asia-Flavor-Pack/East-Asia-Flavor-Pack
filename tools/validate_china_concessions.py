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
    entry_force = unquoted(treaties).split("on_entry_into_force = {", 1)[1].split("on_enforced", 1)[0]
    assert "eafp_concession_grant_effect = yes" in entry_force
    # The JE is visible while inactive and activates by itself once an in-force concession
    # treaty exists (a shown JE activates when possible is true); nothing activates it by script.
    assert re.search(r"is_shown_when_inactive\s*=\s*\{\s*always\s*=\s*yes\s*\}", je_code)
    assert re.search(r"possible\s*=\s*\{\s*eafp_concession_treaty_exists\s*=\s*yes\s*\}", je_code), \
        "Activation is based on an in-force concession treaty"
    treaty_exists = unquoted(read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt"))
    treaty_exists = treaty_exists.split("\neafp_concession_treaty_exists = {", 1)[1].split("\n}", 1)[0]
    assert "any_scope_treaty" in treaty_exists and "has_type = eafp_grant_concession" in treaty_exists
    assert not re.search(r"\badd_contextless_journal_entry\s*=\s*je_concessions_in_china", clean)
    # Pinned for involved countries only.
    for pin in ("should_be_pinned_by_default_involved = yes", "should_be_pinned_by_default_uninvolved_or_context = no"):
        assert pin in je_code, pin
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
    # Ownership transfer: remaining holders get a treaty with the new owner (binding 0 days,
    # no duplicate), and only the current owner's treaty can return the right on withdrawal.
    assert re.search(r"on_withdrawal\s*=\s*\{.*?limit = \{ scope:article\.source_country = scope:concession_host \}.*?"
                     r"eafp_concession_return_effect = \{ FORCED = yes \}", unquoted(treaties), re.S)
    transfer = effects.split("eafp_concession_transfer_treaties_effect = {", 1)[1].split("\n}", 1)[0]
    for clause in ("NOT = { this = scope:eafp_transfer_owner }", "source_country = scope:eafp_transfer_owner",
                   "input_state = scope:eafp_transfer_state", "HOST = scope:eafp_transfer_owner",
                   "HOLDER = scope:eafp_transfer_holder", "STATE = scope:eafp_transfer_state"):
        assert clause in transfer, clause
    create_treaty = effects.split("\neafp_concession_create_treaty_effect = {", 1)[1].split("\n}", 1)[0]
    for clause in ("$HOST$ = {", "first_country = $HOST$", "second_country = $HOLDER$", "is_draft = no",
                   "binding_period = { days = 0 }", "article = eafp_grant_concession", "source_country = $HOST$",
                   "target_country = $HOLDER$", "{ state = $STATE$ }"):
        assert clause in create_treaty, clause
    # When a lapsed article ends a treaty, its other still-valid concession articles get
    # their own treaty instead of returning the right.
    withdrawal = unquoted(treaties).split("on_withdrawal = {", 1)[1].split("on_break", 1)[0]
    assert re.search(r"any_scope_article = \{\s*has_type = eafp_grant_concession\s*source_country = scope:concession_host\s*"
                     r"NOT = \{ input_state \?= \{ owner = scope:concession_host \} \}", withdrawal)
    assert withdrawal.index("eafp_concession_create_treaty_effect") < withdrawal.index("eafp_concession_return_effect = { FORCED = yes }")
    assert "STATE = scope:concession_state" in withdrawal
    state_hook = hooks.split("eafp_concessions_state_changed = {", 1)[1].split("\n}", 1)[0]
    assert state_hook.index("eafp_concession_refresh_effect = yes") < state_hook.index("eafp_concession_transfer_treaties_effect = yes")
    # The previous owner's treaty is not withdrawn by script; its article stops being
    # fulfilled once its source no longer owns the state and the treaty ends as a breach.
    assert "withdraw = {" not in transfer, "Transfer must not withdraw the old treaty directly"
    assert re.search(r"non_fulfillment\s*=\s*\{\s*consequences\s*=\s*withdraw\s*max_consecutive_contraventions\s*=\s*0\s*"
                     r"conditions\s*=\s*\{\s*weekly\s*=\s*\{\s*NOT = \{ scope:article\.input_state \?= \{ owner = root \} \}",
                     unquoted(treaties)), "Old owner's article must lapse through non_fulfillment"
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

    # Reach (interest marker, or play/war against the owner) gates proposals and demands only;
    # the grant effect re-checks the rest, so an enforced demand survives the play's end.
    triggers_code = unquoted(read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt"))
    can_grant = triggers_code.split("eafp_concession_can_grant = {", 1)[1].split("\n}", 1)[0]
    for clause in ("eafp_concession_can_receive = { HOLDER = $HOLDER$ }", "has_interest_marker_in_region = prev.region",
                   "is_diplomatic_play_enemy_of = prev.owner", "has_war_with = prev.owner"):
        assert clause in can_grant, clause
    assert "has_interest_marker_in_region" not in triggers_code.split("\neafp_concession_can_receive = {", 1)[1].split("\n}", 1)[0]
    assert "eafp_concession_can_receive = { HOLDER = scope:concession_holder }" in effects.split("eafp_concession_grant_effect = {", 1)[1]
    # AI: coercive flags as on treaty_port, Second Opium War / Tianjin war-goal weighting.
    assert re.search(r"flags\s*=\s*\{\s*can_be_enforced\s+hostile\s+ai_consider_threaten_naval_hostilities\s*\}", unquoted(treaties))
    assert "is_diplomatic_play_type = dp_second_opium_war" in treaties and "state_region = s:STATE_BEIJING" in treaties
    # Concession demand play (like dp_take_treaty_port): a lens play whose primary war goal,
    # when enforced, creates a real in-force treaty with the concession article.
    demand_play = unquoted(read(ROOT / "common/diplomatic_plays/eafp_concessions_diplomatic_plays.txt"))
    demand_play = demand_play.split("dp_eafp_demand_concession = {", 1)[1].split("\n}", 1)[0]
    assert "war_goal = eafp_demand_concession" in demand_play and "selectable_in_lens" not in demand_play
    war_goals = unquoted(read(ROOT / "common/war_goal_types/eafp_concessions_war_goals.txt"))
    demand_goal = war_goals.split("eafp_demand_concession = {", 1)[1].split("\n}", 1)[0]
    for clause in ("kind = custom", "target_type = state", "contestion_type = control_target_state",
                   "eafp_concession_can_receive = { HOLDER = root }", "is_draft = no",
                   "article = eafp_grant_concession", "source_country = scope:target_country",
                   "target_country = root", "{ state = scope:target_state }"):
        assert clause in demand_goal, clause
    assert "eafp_concession_grant_effect" not in demand_goal, "Grant only through the treaty's on_entry_into_force"

    # Demand/article conditions mirror vanilla treaty_port / take_treaty_port without the
    # treaty-port-only ones, plus China Proper and an unrecognized state owner.
    vanilla_goal = read(game / "common/war_goal_types/25_take_treaty_port.txt")
    vanilla_settings = set(re.findall(r"\w+", vanilla_goal.split("settings = {", 1)[1].split("}", 1)[0].split("#")[0]
                                      + " ".join(l.split("#")[0] for l in vanilla_goal.split("settings = {", 1)[1].split("}", 1)[0].splitlines())))
    goal_settings = set(re.findall(r"\w+", demand_goal.split("settings = {", 1)[1].split("}", 1)[0]))
    assert goal_settings == vanilla_settings - {"validate_take_treaty_port"}, goal_settings ^ (vanilla_settings - {"validate_take_treaty_port"})
    triggers_text = unquoted(read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt"))
    grantable = triggers_text.split("\neafp_concession_eligible_state = {", 1)[1].split("\n}", 1)[0]
    for clause in ("is_in_geographic_region = geographic_region_china_proper", "is_treaty_port = no",
                   "owner = { is_country_type = unrecognized }"):
        assert clause in grantable, clause
    assert "eafp_concession_eligible_state = yes" in triggers_text.split("\neafp_concession_can_receive = {", 1)[1].split("\n}", 1)[0]
    article_code = unquoted(treaties).split("eafp_grant_concession = {", 1)[1]
    for clause in ("unlocked_by_technologies = {\n\t\tcolonization", "is_revolutionary = no",
                   "NOT = { is_subject_of = root }", "exists = scope:article.input_state",
                   "country_rank <= scope:target_country.country_rank",
                   "eafp_concession_can_receive = { HOLDER = scope:other_country }"):
        assert clause in article_code.replace("\r\n", "\n"), clause
    for specific in ("is_potential_treaty_port", "is_coastal", "controls_treaty_port_province"):
        assert specific not in article_code + demand_goal, specific
    assert "any_scope_state = { eafp_concession_eligible_state = yes }" in demand_play
    strategy = unquoted(read(ROOT / "common/ai_strategies/eafp_default_strategy.txt"))
    assert re.search(r"wargoal_scores\s*=\s*\{.*?\beafp_demand_concession\s*=\s*\{", strategy, re.S), "AI score"
    # Second Opium War: third parties can join, and Britain demands Tianjin as a primary demand.
    plays = unquoted(read(ROOT / "common/diplomatic_plays/eafp_diplomatic_plays.txt"))
    second_play = plays.split("dp_second_opium_war = {", 1)[1].split("\n}", 1)[0]
    for setting in ("requires_interest_marker = no", "initiator_can_add_war_goals = yes", "target_can_add_war_goals = yes"):
        assert setting in second_play, setting
    second_war = unquoted(read(ROOT / "events/eafp_chi_events/eafp_second_opium_war_events.txt"))
    assert re.search(r"add_war_goal\s*=\s*\{\s*holder = c:GBR\s*type = enforce_treaty_article\s*target_country = c:CHI\s*"
                     r"primary_demand = yes\s*article\s*=\s*\{\s*article = eafp_grant_concession[^}]*"
                     r"inputs\s*=\s*\{\s*\{\s*state = s:STATE_BEIJING\.region_state:CHI", second_war), "Tianjin primary demand"
    assert "source_modifier" not in treaties and "target_modifier" not in treaties
    # Treasury charges: paid concession expansion and the monthly company industry investment.
    assert effects.count("add_treasury") == 2, "Only expansion and industry investment charge the treasury"
    # The weekly Chinese-treasury-to-holder transfer and its modifiers are removed entirely.
    assert not re.search(r"\bconcession_pa(?:yment|id)\b", clean), \
        "No recurring treasury transfer from the Chinese owner to holders"
    assert "EAFP_CONCESSION_AI_INCOME" not in treaties, "Treaty AI must not value a removed transfer"
    # Influence cost equals vanilla treaty_port; a successful grant adds +1000 involvement.
    vanilla_port_cost = re.search(r"^\s*cost\s*=\s*(\d+)", read(game / "common/treaty_articles/14_treaty_port.txt"), re.M)[1]
    assert re.search(r"^\s*cost\s*=\s*(\d+)", unquoted(treaties), re.M)[1] == vanilla_port_cost, "Influence cost = treaty_port"
    grant_body = effects.split("eafp_concession_grant_effect = {", 1)[1].split("\n}", 1)[0]
    assert grant_body.index("add_to_variable_list = { name = concession_owner_varlist target = scope:concession_holder }") \
        < grant_body.index("add_involvement = { strategic_region = scope:concession_region value = 1000 }"), \
        "Involvement only after the right is registered"
    assert "building_trade_center" not in unquoted(effects), "No vanilla trade center reward or deletion"
    # Grant and paid expansion both move in steps of 5 levels.
    assert effects.count("eafp_concession_add_company_level = { LEVELS = 5 }") == 2
    assert "LEVELS = 1 }" not in effects
    # Concession levels are only company-owned: one create_building, no country-ownership fallback,
    # and an owner without a company gets one the same way a treaty grant does.
    assert effects.count("levels = $LEVELS$") == 1
    assert "add_ownership = { country =" not in unquoted(effects)
    ensure = effects.split("eafp_concession_ensure_company = {", 1)[1].split("\n}", 1)[0]
    for clause in ("add_modifier = { name = eafp_concession_company_slot }",
                   "add_company = company_type:company_eafp_concession",
                   "set_company_state_region = scope:concession_company_hq"):
        assert clause in ensure, clause
    assert effects.count("add_company = company_type:company_eafp_concession") == 1
    assert "scope:concession_holder = { eafp_concession_ensure_company = yes }" in effects.split("eafp_concession_grant_effect = {", 1)[1]
    assert "scope:eafp_rebuild_owner = { eafp_concession_ensure_company = yes }" in effects.split("eafp_concession_rebuild_create = {", 1)[1]
    grant_gate = read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt").split("eafp_concession_can_grant = {", 1)[1].split("eafp_concession_has_holder = {", 1)[0]
    assert "eafp_concession_free_capacity >= 5" in grant_gate
    assert "add_company = company_type:company_eafp_concession" in effects
    assert "remove_company = company_type:company_eafp_concession" in effects
    assert "NOT = { eafp_concession_holder_has_rights = yes }" in effects
    assert "eafp_concession_expand_effect = yes" in je_code
    # AI expansion waits until the concession building is staffed enough.
    ai_expand = je_code.split("ordered_in_global_list = {", 1)[1].split("eafp_concession_expand_effect = yes", 1)[0]
    assert re.search(r"is_building_type = building_eafp_concession\s*occupancy >= eafp_concession_ai_expand_min_occupancy", ai_expand)
    assert re.search(r"^eafp_concession_ai_expand_min_occupancy = \{ value = 0\.8 \}",
                     read(ROOT / "common/script_values/eafp_concessions_values.txt"), re.M)
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
    # Only the return (last right / per-holder share removal) and the rightless-state refresh
    # remove the building.
    assert re.findall(r"remove_building\s*=\s*(\w+)", unquoted(effects + je)) == ["building_eafp_concession"] * 3
    # A return with other rights left removes only the returning holder's share: every other
    # owner is stored, the building removed, and each stored owner recreated.
    share = effects.split("eafp_concession_remove_holder_share = {", 1)[1].split("\n}", 1)[0]
    assert "limit = { NOT = { this = scope:concession_holder } }" in share
    assert share.index("eafp_concession_measure_country_levels = { COUNTRY = scope:eafp_rebuild_owner }") \
        < share.index("remove_building = building_eafp_concession") \
        < share.index("eafp_concession_rebuild_owner_levels = yes"), "Store others, remove, recreate"
    returning = effects.split("eafp_concession_return_effect = {", 1)[1].split("\n}", 1)[0]
    assert re.search(r"else_if\s*=\s*\{\s*limit\s*=\s*\{\s*has_building\s*=\s*building_eafp_concession\s*\}"
                     r"(?:\s*#[^\n]*)*\s*eafp_concession_remove_holder_share\s*=\s*yes", returning)
    assert "residual assets retained" not in effects
    # Increase = overwrite the holder's ownership on the live building (user design 2026-11-11).
    rebuild = effects.split("eafp_concession_add_company_level = {", 1)[1].split("\n}", 1)[0]
    assert "remove_building" not in unquoted(rebuild), "Expansion must not remove the building"
    assert "flag:cash_reserve" not in effects and "cash_reserves_ratio" not in effects
    assert "clear_variable_map = eafp_concession_rebuild_map" in rebuild
    assert "eafp_concession_rebuild_map_add = { KEY = scope:concession_holder VALUE = scope:eafp_rebuild_added }" in rebuild
    assert rebuild.index("eafp_concession_measure_country_levels = { COUNTRY = scope:concession_holder }") \
        < rebuild.index("eafp_concession_rebuild_owner_levels = yes"), "Read the holder's levels, then overwrite"
    # return, per-holder share removal, rounding, the industry investment (holder pick + building
    # share) and the urban usage record.
    assert effects.count("eafp_concession_measure_country_levels = { COUNTRY =") == 7
    # State creation/owner change rounds split shares to the nearest multiple of 5 (min 5)
    # by overwriting, never by removing the building.
    rounding = effects.split("eafp_concession_round_ownership_effect = {", 1)[1].split("\n}", 1)[0]
    assert "value = { value = scope:concession_level_low divide = 5 round = yes multiply = 5 min = 5 }" in rounding
    assert "NOT = { scope:eafp_rebuild_rounded = scope:concession_level_low }" in rounding
    assert "remove_building" not in unquoted(rounding)
    assert rounding.index("eafp_concession_measure_country_levels") < rounding.index("eafp_concession_rebuild_owner_levels = yes")
    state_hook = hooks.split("eafp_concessions_state_changed = {", 1)[1].split("\n}", 1)[0]
    assert state_hook.index("eafp_concession_round_ownership_effect = yes") < state_hook.index("eafp_concession_refresh_effect = yes")
    assert re.search(r"on_state_owner_change\s*=\s*\{\s*on_actions\s*=\s*\{\s*eafp_concessions_state_changed", entries)
    assert re.search(r"on_state_created\s*=\s*\{\s*on_actions\s*=\s*\{\s*eafp_concessions_state_changed", entries)
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
    # Monthly industry investment: the concession company gets one level at once (no private
    # construction queue), paid by the holder only when its share grew; ports are included.
    assert "start_privately_funded_building_construction" not in clean
    assert "eafp_concession_industry_investment_effect = yes" in je_code
    invest = effects.split("eafp_concession_industry_investment_effect = {", 1)[1].split("\n}", 1)[0]
    invest_types = re.findall(r"eafp_concession_industry_create = \{ TYPE = (\w+) \}", invest)
    assert invest_types and len(invest_types) == len(set(invest_types)) and "building_port" in invest_types
    vanilla_buildings = "\n".join(read(p) for p in (game / "common/buildings").glob("*.txt"))
    for key in invest_types:
        assert re.search(r"^" + key + r"\s*=", vanilla_buildings, re.M), key
        assert "can_construct_building = " + key in invest, key
    assert "gold_reserves >= eafp_concession_industry_level_cost" in invest
    # Only a company owning concession levels in this very state is chosen (best starts at 0,
    # measured on this state's concession building, strictly greater wins).
    assert "save_temporary_scope_value_as = { name = eafp_industry_best value = 0 }" in invest
    assert "scope:eafp_industry_concession = { eafp_concession_measure_country_levels = { COUNTRY = scope:eafp_industry_candidate } }" in invest
    assert re.search(r"limit = \{\s*scope:concession_level_low > scope:eafp_industry_best\s*scope:eafp_industry_used < scope:concession_level_low\s*\}", invest), "Cap: urban levels below concession levels"
    # Usage record: refreshed weekly and before each investment, counting exactly the
    # investable building types.
    assert invest.index("eafp_concession_urban_usage_refresh = yes") < invest.index("every_in_list")
    assert "variable_map(eafp_concession_urban_map|scope:eafp_industry_candidate)" in invest
    refresh_body = effects.split("eafp_concession_refresh_effect = {", 1)[1].split("\n}", 1)[0]
    assert "eafp_concession_urban_usage_refresh = yes" in refresh_body
    usage = effects.split("eafp_concession_urban_usage_refresh = {", 1)[1].split("\n}", 1)[0]
    assert "add_to_variable_map = { name = eafp_concession_urban_map key = scope:eafp_usage_holder" in usage
    urban_trigger = unquoted(read(ROOT / "common/scripted_triggers/eafp_concessions_triggers.txt"))
    urban_trigger = urban_trigger.split("\neafp_concession_urban_investment_building = {", 1)[1].split("\n}", 1)[0]
    assert sorted(re.findall(r"is_building_type = (\w+)", urban_trigger)) == sorted(
        re.findall(r"eafp_concession_industry_create = \{ TYPE = (\w+) \}", invest)), "Cap counts the investable types"
    assert invest.index("eafp_concession_industry_create") < invest.index("add_treasury"), "Charge after the grant"
    assert re.search(r"levels_owned_by_country = \{ target = scope:eafp_industry_holder value >= scope:eafp_industry_new_levels \}\s*\}\s*scope:eafp_industry_holder = \{ add_treasury", invest)
    create = effects.split("eafp_concession_industry_create = {", 1)[1].split("\n}", 1)[0]
    levels = [int(x) for x in re.findall(r"^\t\t(\d+) = \{ create_building = \{ building = \$TYPE\$ add_ownership = \{ company = \{ type = company_eafp_concession", create, re.M)]
    assert levels == list(range(1, 101)), "One literal case per level 1..100"
    # Costs (user values): industry level 100,000; +5 concession expansion 500,000.
    values_text = read(ROOT / "common/script_values/eafp_concessions_values.txt")
    assert re.search(r"^eafp_concession_industry_level_cost = \{ value = 100000 \}", values_text, re.M)
    assert re.search(r"^eafp_concession_expansion_cost = \{ value = 500000 \}", values_text, re.M)
    # Industry investment needs a staffed, funded concession building; looser than AI expansion.
    invest_call = je_code.split("eafp_concession_industry_investment_effect = yes", 1)[0].rsplit("every_in_global_list = {", 1)[1]
    assert "occupancy >= eafp_concession_industry_min_occupancy" in invest_call
    assert "cash_reserves_ratio >= eafp_concession_industry_min_cash_reserves" in invest_call
    num = lambda key: float(re.search(r"^" + key + r" = \{ value = ([\d.]+) \}", values_text, re.M)[1])
    assert num("eafp_concession_industry_min_occupancy") < num("eafp_concession_ai_expand_min_occupancy")
    assert 0 < num("eafp_concession_industry_min_cash_reserves") < 1
    # Every candidate building, ports included, needs a positive weekly profit.
    invest_limit = invest.split("ordered_scope_building = {", 1)[1].split("order_by", 1)[0]
    assert re.search(r"^\t\t\t\tweekly_profit > 0$", invest_limit, re.M) and "building_port" in invest_limit
    assert not re.search(r"OR = \{\s*weekly_profit > 0\s*is_building_type = building_port", invest_limit)
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
    # [concept_concession] is used throughout the UI text, so the game concept must exist.
    concepts = "\n".join(unquoted(read(p)) for p in (ROOT / "common/game_concepts").glob("*.txt"))
    assert len(re.findall(r"^concept_concession\s*=\s*\{", concepts, re.M)) == 1, "Missing/duplicate concept_concession"
    concept_icon = re.search(r'concept_concession\s*=\s*\{[^}]*texture\s*=\s*"([^"]+)"',
                             "\n".join(read(p) for p in (ROOT / "common/game_concepts").glob("*.txt")))
    assert concept_icon and ((ROOT / concept_icon[1]).is_file() or (game / concept_icon[1]).is_file()
                             or args.source_only), ("Missing concept icon", concept_icon and concept_icon[1])
    assert set(re.findall(r"is_in_geographic_region\s*=\s*(\w+)", clean)) == {region}, \
        "Concession geography must use China Proper"
    assert re.search(r"eafp_concession_eligible_state\s*=\s*\{\s*"
                     r"is_in_geographic_region\s*=\s*" + region + r"\b", gates)
    if not args.source_only:
        for asset in set(re.findall(r'(?:icon|texture|video)\s*=\s*"?([^"\s{}]+)', code)):
            if asset.startswith("["):
                continue  # data-bound GUI texture such as [Company.GetCompanyType.GetIcon]
            assert (ROOT / asset).is_file() or (game / asset).is_file(), ("Missing asset", asset)

    gui = read(ROOT / "gui/journal_entry_widgets/eafp_concessions_in_china.gui")
    assert 'name = "widget_eafp_concessions"' in gui
    assert je.count('name = "widget_eafp_concessions"') == 1
    # Placed below the JE description; the JE status (default key <je>_status, no status_desc)
    # states how many states have concessions, and the reason no longer does.
    assert re.search(r'name = "widget_eafp_concessions"\s*(?:#[^\n]*\s*)*container = "custom_widget_container_5"', je)
    assert "status_desc" not in je_code
    count_expr = "[GetDataModelSize(GetGlobalList('concession_candidate_states_gvarlist'))]"
    for lang in LANGUAGES:
        china_loc = read(ROOT / f"localization/{lang}/eafp_concessions_in_china_l_{lang}.yml")
        status = re.search(r'^\s*je_concessions_in_china_status:\s*"(.*)"\s*$', china_loc, re.M)
        reason = re.search(r'^\s*je_concessions_in_china_reason:\s*"(.*)"\s*$', china_loc, re.M)[1]
        assert status and count_expr in status[1] and count_expr not in reason, lang
    sgui = read(ROOT / "common/scripted_guis/concessions_in_china_sgui.txt")
    assert "JournalEntry.GetCountry" not in gui and "viewer" not in gui + sgui, \
        "All observers must see the same international overview"
    assert "scripted_button" not in je
    # The international widget reads live state and ownership; per-state expansion is UI-only
    # (vanilla building-browser style: each row toggles on its own state ID).
    toggle_key = "Concatenate('eafp_concession_state_', State.GetIDString)"
    assert f"GetVariableSystem.Toggle({toggle_key})" in gui and f"GetVariableSystem.Exists({toggle_key})" in gui
    # The JE widget holds only the state rows (no heading, hint or empty-list text).
    widget_root = gui.split('name = "widget_eafp_concessions"', 1)[1]
    assert re.findall(r"^\t(\w+)\s*=", widget_root, re.M) == [
        "direction", "ignoreinvisible", "using", "min_width", "max_width", "margin", "background",
        "eafp_concession_state_rows"]
    # Fixed width and frame matching the vanilla JE containers (@panel_width_minus_30 = 510).
    journal_gui = read(game / "gui/journal_entry.gui")
    assert "min_width = @panel_width_minus_30" in journal_gui and "using = entry_bg" in journal_gui
    for clause in ("using = default_list_position", "min_width = 510", "max_width = 510",
                   "background = { using = entry_bg }"):
        assert clause in widget_root, clause
    # Expanded details sit on the dark inset used by the building browser's construction area.
    # The details container is the one whose visibility is the per-state toggle and which
    # holds the ownership bar (located by markup, not by comments).
    details_match = re.search(r"flowcontainer = \{\s*visible = \"\[GetVariableSystem\.Exists\(" + re.escape(toggle_key)
                              + r"\)\]\"(?:(?!\n\t\t\t\t\}).)*", gui, re.S)
    assert details_match and "eafp_concession_ownership_bar = {" in details_match[0], "Details container not found"
    details = details_match[0]
    assert "background = { using = dark_area }" in details
    # New concession buildings start with zero cash reserves.
    assert re.findall(r"RESERVES = (\S+) \}", effects) == ["0"], "Only reserves = 0 is used"
    # Concession levels are only company-owned, so the widget handles company ownership alone.
    assert "IsCountryOwned" not in gui and "GetOwnerCountry" not in gui
    # One ownership bar per state, split by ownership entry and coloured by the company's country.
    bar = gui.split("type eafp_concession_ownership_bar = v3_stacked_barchart {", 1)[1].split("\n\t}", 1)[0]
    for clause in ("datamodel = \"[Building.GetBuildingOwnerships]\"", "BuildingOwnership.GetOwnershipRatio",
                   "datacontext = \"[BuildingOwnership.GetOwnerBuilding.GetCompany]\""):
        assert clause in bar, clause
    assert "color = \"[Company.GetCountry.GetMapColor]\"" in gui.split("type eafp_concession_owner_segment = widget {", 1)[1]
    owner_row = gui.split("type eafp_concession_owner_row = flowcontainer {", 1)[1].split("\n\t}", 1)[0]
    assert "datacontext = \"[BuildingOwnership.GetOwnerBuilding.GetCompany]\"" in owner_row
    # No layout boxes in the widget's own markup (vanilla types may use them internally).
    assert not re.search(r"\b[hv]box\s*=", gui), "Use container/flowcontainer, not hbox/vbox"
    # The two country-colour bars are 8 px backgrounds of the fixed-width (480) row, so they
    # always span its full height: one shrunk from the right, one from the left.
    assert "minimumsize = { 480 -1 }" in owner_row
    assert re.search(r"margin_left = 16\s*margin_right = 16", owner_row)
    for side in ("margin_right", "margin_left"):
        assert re.search(r"background = \{\s*using = entry_bg_simple_colored\s*color = \"\[Company\.GetCountry\.GetMapColor\]\"\s*"
                         + side + r" = -472\s*\}", owner_row), side
    assert owner_row.count("Company.GetCountry.GetMapColor") == 2
    assert not re.search(r"size = \{ 8 \d+ \}", owner_row), "No fixed-height colour bars"
    assert "IsCountryOwned" not in owner_row
    # Under each company: the state's buildings (minus the concession building) in which that
    # company owns levels, each line opening the building with its vanilla tooltip.
    assert 'datamodel = "[State.AccessBuildings]"' in owner_row
    # The usage line toggles the list (per state x company, collapsed by default).
    company_key = "Concatenate(Concatenate('eafp_concession_company_', State.GetIDString), Company.GetCountry.GetIDString)"
    assert f"onclick = \"[GetVariableSystem.Toggle({company_key})]\"" in owner_row
    assert re.search(r'section_header_button = \{\s*tooltip = "eafp_concession_urban_usage_tt"', owner_row)
    # Normal text size: the header's default fontsize_large is overridden with nothing.
    assert re.search(r'blockoverride "fontsize" \{\}\s*blockoverride "left_text" \{ text = "eafp_concession_urban_usage" \}', owner_row)
    assert re.search(r'flowcontainer = \{\s*visible = "\[GetVariableSystem\.Exists\(' + re.escape(company_key)
                     + r'\)\]"(?:(?!flowcontainer = \{).)*datamodel = "\[State\.AccessBuildings\]"', owner_row, re.S)
    assert "visible = \"[Not(ObjectsEqual(Building.Self, State.GetBuilding('building_eafp_concession').Self))]\"" in owner_row
    assert 'visible = "[ObjectsEqual(BuildingOwnership.GetOwnerBuilding.GetCompany.Self, Company.Self)]"' in owner_row
    building_row = gui.split("type eafp_concession_company_building_row = button {", 1)[1].split("\n\t}", 1)[0]
    for clause in ('onclick = "[InformationPanelBar.OpenBuildingDetailsPanel(Building.AccessSelf)]"',
                   "FancyTooltip_Building = {}", 'text = "eafp_concession_company_building_row"'):
        assert clause in building_row, clause
    assert "eafp_concession_ownership_bar = {" in gui.split("types eafp_concession_widgets", 1)[1].split("type eafp_concession_state_rows", 1)[1]
    # Navigation to the state and to the concession building.
    assert "onclick = \"[InformationPanelBar.OpenStatePanel(State.AccessSelf)]\"" in gui
    assert "datacontext = \"[State.GetBuilding('building_eafp_concession')]\"" in gui
    assert "onclick = \"[InformationPanelBar.OpenBuildingDetailsPanel(Building.AccessSelf)]\"" in gui
    # Each navigation button shows the vanilla object tooltip of its target.
    for onclick, fancy in (("OpenStatePanel(State.AccessSelf)", "FancyTooltip_State"),
                           ("OpenBuildingDetailsPanel(Building.AccessSelf)", "FancyTooltip_Building"),
                           ("OpenCountryPanel(Country.Self)", "FancyTooltip_Country"),
                           ("OpenCompanyPanel(Company.Self)", "FancyTooltip_Company")):
        assert re.search(re.escape(onclick) + r"\]\"\s*tooltipwidget\s*=\s*\{\s*" + fancy + r"\s*=\s*\{\s*\}", gui), fancy
        assert re.search(r"^\s*type " + fancy + r" = ", "\n".join(read(p) for p in (game / "gui").rglob("*.gui")), re.M), fancy
    assert "eafp_concession_goto_" not in gui, "Plain-text go-to tooltips were replaced"
    # Expansion requirements shown on the button: right, urban cap room, gold reserves, ownership.
    can_expand = triggers_code.split("\neafp_concession_can_expand = {", 1)[1].split("\n}", 1)[0]
    assert re.findall(r"text = (eafp_concession_expand_\w+_tt)", can_expand) == [
        "eafp_concession_expand_active_tt", "eafp_concession_expand_capacity_tt",
        "eafp_concession_expand_treasury_tt", "eafp_concession_expand_ownership_tt"]
    assert "$HOLDER$ = { gold_reserves >= eafp_concession_expansion_cost }" in can_expand
    # Expand button: vanilla JE action tooltip shape (requirements with checkmarks, then effects).
    assert 'tooltip = "eafp_concession_expand_button_tt"' in gui
    sgui_code = unquoted(read(ROOT / "common/scripted_guis/concessions_in_china_sgui.txt"))
    assert re.search(r"show_as_tooltip\s*=\s*\{\s*scope:actor\s*=\s*\{\s*add_treasury\s*=\s*\{\s*value = eafp_concession_expansion_cost multiply = -1", sgui_code), \
        "Display-only fee line; the fee is charged inside the effect"
    for lang in LANGUAGES:
        expand_tt = re.search(r'^\s*eafp_concession_expand_button_tt:\s*"(.*)"\s*$',
                              read(ROOT / f"localization/{lang}/eafp_concessions_in_china_l_{lang}.yml"), re.M)[1]
        assert expand_tt.index("$TOOLTIP_DELIMITER$") < expand_tt.index(".IsValidTooltip(") \
            < expand_tt.index("#title") < expand_tt.index(".ExecuteTooltip("), lang
    assert gui.count("{") == gui.count("}"), "Unbalanced braces in the widget"
    # Bar segments: the flag opens the country panel, the company logo the company panel.
    segment = gui.split("type eafp_concession_owner_segment = widget {", 1)[1].split("\n\t}", 1)[0]
    assert "datacontext = \"[Company.GetCountry]\"" in segment
    assert "onclick = \"[InformationPanelBar.OpenCountryPanel(Country.Self)]\"" in segment
    assert "texture = \"[Company.GetCompanyType.GetIcon]\"" in segment and "[InformationPanelBar.OpenCompanyPanel(Company.Self)]" in segment
    # The header's current/cap figure explains the cap.
    assert re.search(r'text = "eafp_concession_card_total"\s*tooltip = "eafp_concession_cap_tt"', gui)
    # Details keep only the ownership bar/list and the expansion button.
    for removed in ("eafp_concession_cap_status", "progressbar", "concession_owner_varlist", "eafp_concession_rights_heading"):
        assert removed not in details, removed
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
            and k not in ("eafp_concession_compensation", "eafp_concession_rebuild_map",
                          "eafp_concession_urban_map")}
    for key in ("je_concessions_in_china",):
        keys.update((key, key + "_reason", key + "_status"))
    for key in ("eafp_grant_concession",):
        # The article's _desc text was removed on purpose (2026-11-11); no code references it.
        keys.update(key + suffix for suffix in ("", "_effects_desc", "_article_short_desc"))
    keys.update(("concept_concession", "concept_concessions", "concept_concession_desc",
                 "eafp_concession_expand_title", "eafp_concession_expand_desc"))
    # Concessions work regardless of the host's and holder's prestige: no prestige comparison
    # anywhere in the feature, and no active/suspended status in the widget.
    assert not re.search(r"\bprestige\s*(?:[<>]=?|=)\s*\S*prestige", clean), "Prestige must not gate concessions"
    for removed in ("eafp_concession_holder_active_gui", "eafp_concession_activity_summary",
                    "eafp_concession_prestige_tt", "eafp_concession_active_label"):
        assert removed not in code, removed
    # A concession right always works through the building: no separate operation check.
    assert not re.search(r"\beafp_concession_active\b|eafp_concession_active_holder_count", clean), \
        "Operation checks were removed"
    assert "eafp_concession_has_holder = { HOLDER = scope:concession_holder }" in \
        triggers_text.split("\neafp_concession_event_valid = {", 1)[1].split("\n}", 1)[0]
    assert "eafp_concession_has_holder = { HOLDER = $HOLDER$ }" in \
        triggers_text.split("\neafp_concession_can_expand = {", 1)[1].split("\n}", 1)[0]
    eligible_users = {p.name for p in files if "eafp_concession_eligible_state = yes" in read(p)}
    assert eligible_users <= {"eafp_concessions_triggers.txt", "eafp_concessions_treaty_articles.txt",
                              "eafp_concessions_diplomatic_plays.txt"}, eligible_users
    assert "eafp_concession_eligible_state" not in je_code, "The eligibility check gates grants only"
    keys.update(key for key in feature_definitions
                if key.startswith(("building_eafp_", "bg_eafp_", "company_eafp_", "pm_eafp_", "pmg_eafp_")))
    keys.update(("eafp_concession_company_slot", "eafp_concession_forced_loss", "eafp_concession_right_live", "eafp_concession_right_returned"))
    keys.update("war_goal_eafp_concession_incident_return" + s
                for s in ("", "_type_name", "_type_desc", "_desc", "_sway_desc"))
    keys.update("dp_eafp_concession_incident" + s for s in ("", "_desc", "_tooltip"))
    keys.update("war_goal_eafp_demand_concession" + s
                for s in ("", "_type_name", "_type_desc", "_desc", "_sway_desc"))
    keys.update("dp_eafp_demand_concession" + s for s in ("", "_desc", "_tooltip"))
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
        # All concession localization lives in one file per language (merged 2026-11-12).
        path = ROOT / "localization" / lang / f"eafp_concessions_in_china_l_{lang}.yml"
        structural_check(path)
        assert read(path).splitlines()[0] == "l_" + lang + ":"
        assert not (ROOT / "localization" / lang / f"eafp_concessions_buildings_l_{lang}.yml").exists()
        own = set(re.findall(r'^\s*([\w.]+):', read(path), re.M))
        assert keys <= own, ("Concession key outside the concession file", lang, sorted(keys - own)[:5])
        # No unused text: every key is required above, referenced from another entry
        # ($key$ or a SelectLocalization branch), or a loaded event's text.
        own_text = read(path)
        nested = set(re.findall(r"\$(\w+)\$", own_text)) | set(re.findall(r"'(eafp_concession_\w+)'", own_text))
        loaded_events = set(re.findall(r"^(concessions_in_china\.\d+)\s*=", clean, re.M))
        # Names of script definitions (building, PM group, company, modifier...) are read by the engine.
        unused = {k for k in own - keys - nested - {"l_" + lang}
                  if not (k.rsplit(".", 1)[0] in loaded_events) and not definitions[k]}
        assert not unused, ("Unused concession localization", lang, sorted(unused))
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
          "Known limitations: per-holder share removal rebuilds the building (workforce re-hired); "
          "partial production suspension is unavailable.")


if __name__ == "__main__":
    main()

