"""Source regressions for the 1.15 P1 migration; does not emulate the game engine.

The small state-predicate evaluator below reads the actual inline ownership
conditions. It covers the donor/HQ/capital/split/player cases that caused the old
button/event mismatch, rather than testing a second implementation of that rule.
"""
from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import re
import subprocess

from journal_schema import entries, named, normalized, tokens

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return path.read_text(encoding='utf-8-sig')


def definition(path, key):
    text = read(path)
    return named(text, key).body(text)


def field(text, key):
    return named(text, key).body(text)


def walk(text, parents=()):
    """Traverse assignment maps, leaving literal lists opaque."""
    try:
        children = entries(text)
    except AssertionError:
        return
    for entry in children:
        yield entry, text, parents
        if entry.value(text).startswith('{'):
            yield from walk(entry.body(text), parents + ((entry, text),))


def baseline(path, ref):
    return subprocess.check_output(
        ['git', 'show', f'{ref}:{path}'], cwd=ROOT
    ).decode('utf-8-sig').replace('\r\n', '\n')


def catalogue(directory):
    result = {}
    for path in directory.rglob('*.txt'):
        text = read(path)
        for entry in entries(text):
            result[entry.key.split(':')[-1]] = (entry, text, path)
    return result


def characters(game, ref):
    vanilla = catalogue(game / 'common/character_templates')
    total = 0
    for path in (ROOT / 'common/character_templates').glob('*.txt'):
        text = read(path)
        old = baseline(path.relative_to(ROOT).as_posix(), ref)
        # This pre-existing malformed EOF is intentionally repaired in P1.
        if path.name == 'eafp_character_templates_KOR.txt':
            old = old.rstrip().removesuffix('s')
        for entry in entries(text):
            key = entry.key.split(':')[-1]
            before = named(old, key).body(old)
            after = entry.body(text)
            old_fields = {e.key for e in entries(before)}
            if entry.key.startswith('REPLACE:') and key in vanilla:
                ve, vt, _ = vanilla[key]
                vb = ve.body(vt)
                religions = [e.value(vb) for e in entries(vb) if e.key == 'religion']
                if religions and 'religion' not in old_fields:
                    assert named(after, 'religion').value(after) == religions[0], key
                    total += 1
                    r = named(after, 'religion')
                    after = after[:r.start] + after[r.end:]
            assert normalized(before) == normalized(after), ('template payload changed', key)
    assert total == 42, total
    roles = {
        'eafp_japan_character_roles.txt': 'yes',
        'eafp_mongolia_character_roles.txt': 'yes',
        'eafp_unique_roles.txt': 'no',
    }
    for filename, allowed in roles.items():
        text = read(ROOT / 'common/character_roles' / filename)
        for entry in entries(text):
            body = entry.body(text)
            assert named(body, 'can_be_interest_group_leader').value(body) == allowed
    emperor = definition(game / 'common/character_roles/02_unique_roles.txt',
                         'character_role_emperor_of_japan')
    assert named(emperor, 'can_be_interest_group_leader').value(emperor) == 'no'
    hui = read(ROOT / 'events/eafp_chi_events/eafp_hui_revolt_events.txt')
    du = [e.body(t) for e, t, _ in walk(hui)
          if e.key == 'create_character' and 'first_name = "Wenxiu"' in e.body(t)]
    assert len(du) == 1 and named(du[0], 'religion').value(du[0]) == 'rel:sunni'
    print('PASS: 42 vanilla religions; all other template payloads preserved; role eligibility; Du Wenxiu.')


def events(game, ref):
    protected_events = 0
    vanilla_events = catalogue(game / 'events')
    for relative in ('events/000_eafp_japan_overrides.txt',
                     'events/soi_events/00_ep1_korea_events.txt'):
        text = read(ROOT / relative)
        old = baseline(relative, ref)
        for event in entries(text):
            if event.key == 'namespace':
                continue
            body = event.body(text)
            original = named(old, event.key).body(old)
            if event.key in vanilla_events and 'never_fire_again_modifier_time' in normalized(original):
                ve, vt, _ = vanilla_events[event.key]
                if 'fire_only_once' in {e.key for e in entries(ve.body(vt))}:
                    assert named(body, 'fire_only_once').value(body) == 'yes', event.key
            if event.key.startswith('korea_monarchy.'):
                assert normalized(body) == normalized(original), event.key
            if 'set_temporary_event_immortality' not in normalized(body):
                continue
            protected_events += 1
            protected = Counter()
            for e, t, parents in walk(field(body, 'immediate')):
                if e.key != 'set_temporary_event_immortality':
                    continue
                scope = None
                for parent, pt in reversed(parents):
                    siblings = parent.body(pt)
                    saves = [x.value(siblings) for x in entries(siblings)
                             if x.key == 'save_scope_as']
                    if saves:
                        scope = 'scope:' + saves[0]
                        break
                    if parent.key.startswith('scope:'):
                        scope = parent.key
                        break
                assert scope, (event.key, 'cannot identify protected character')
                protected[scope] += 1
            after = field(body, 'after')
            released = Counter(re.findall(
                r'revoke_temporary_event_immortality\s*=\s*{\s*CHARACTER\s*=\s*(scope:\w+)', after))
            assert protected == released, (event.key, protected, released)
            for e, t, parents in walk(body):
                if e.key != 'kill_character':
                    continue
                if any(p.key == 'show_as_tooltip' for p, _ in parents):
                    continue  # A preview does not execute the death effect.
                # Intentional deaths in these migrated events revoke protection first.
                scope_parent = next(((p, pt) for p, pt in reversed(parents)
                                     if p.key.startswith('scope:')), None)
                if scope_parent and scope_parent[0].key in protected:
                    scope = scope_parent[0].key
                    effect_map = next((pt for p, pt in reversed(parents) if p.key == scope), '')
                    pos = scope_parent[0].start
                    assert f'CHARACTER = {scope}' in effect_map[:pos], (event.key, scope, 'kill before revoke')
    assert protected_events >= 20, protected_events
    japan = read(ROOT / 'events/000_eafp_japan_overrides.txt')
    for key in ('ep2_meiji_pulse.1', 'ep2_meiji_pulse.3', 'ep2_meiji_pulse.4'):
        b = named(japan, key).body(japan)
        tr = field(b, 'trigger')
        eligibility = field(tr, 'any_in_global_list')
        variable = named(eligibility, 'variable')
        eligibility = eligibility[:variable.start] + eligibility[variable.end:]
        draw = field(field(field(b, 'immediate'), 'random_in_global_list'), 'limit')
        assert normalized(eligibility) == normalized(draw), (key, 'GP draw differs from trigger')
        assert normalized('NOT = { ROOT = this }') in [
            normalized(eligibility[e.start:e.end]) for e in entries(eligibility)]
    b = named(japan, 'ep2_meiji_pulse.3').body(japan)
    for option in [e.body(b) for e in entries(b) if e.key == 'option']:
        option_name = named(option, 'name').value(option)
        # Only the two settlement options have a treaty to show to the GP.
        expected = 0 if option_name == 'ep2_meiji_pulse.3.a' else 1
        assert option.count('id = ep2_meiji_pulse.12') == expected
    korea = read(ROOT / 'events/soi_events/00_ep1_korea_events.txt')
    assert 'is_template_used = KOR_choi_je_woo' in field(named(korea, 'gg_korea.3').body(korea), 'trigger')
    assert named(named(korea, 'gg_korea.4').body(korea), 'fire_only_once')
    assert 'eafp_japan_negotiation_protected' not in japan
    print(f'PASS: {protected_events} protection/release pairs; death order; GP eligibility; foreign followups; inactive Korean stubs.')


@dataclass
class Owner:
    name: str
    player: bool = False
    headquarters: bool = False
    overlord: str = ''
    being_freed: bool = False


@dataclass
class State:
    owner: Owner
    region: str
    capital: bool = False
    split: bool = False


def state_predicate(body, current, donor='QING'):
    """Evaluate only the documented atoms used by the actual ownership guard.

    Unknown atoms fail the test, so changing the script cannot silently bypass
    this matrix. Country diplomacy and the actual engine transfer remain runtime
    tests; this is a narrow source-level ownership regression.
    """
    results = []
    for e in entries(body):
        key, value = e.key, e.value(body)
        if key in ('OR', 'AND', 'NOR', 'NOT', 'NAND'):
            children = entries(e.body(body))
            bits = [state_predicate(e.body(body)[c.start:c.end], current, donor) for c in children]
            result = {'OR': any(bits), 'AND': all(bits), 'NOR': not any(bits),
                      'NOT': not all(bits), 'NAND': not all(bits)}[key]
        elif key == 'owner' and value.startswith('{'):
            result = state_predicate(e.body(body), current.owner, donor)
        elif key == 'owner':
            assert value == '$DONOR$'
            result = current.owner.name == donor
        elif key == 'is_player':
            result = current.player == (value == 'yes')
        elif key == 'is_capital':
            result = current.capital == (value == 'yes')
        elif key == 'is_split_state':
            result = current.split == (value == 'yes')
        elif key == 'is_subject_type':
            assert value == 'subject_type_military_headquarters_china'
            result = current.headquarters
        elif key == 'is_subject_of_and_not_being_freed':
            assert value == '$DONOR$'
            result = current.overlord == donor and not current.being_freed
        elif key == 'state_region':
            result = current.region == value.removeprefix('s:')
        else:
            raise AssertionError(('unsupported ownership atom', key, value))
        results.append(result)
    return all(results)


def russia(game):
    triggers = read(ROOT / 'common/scripted_triggers/eafp_russo_chinese_triggers.txt')
    # This identifier already exists in vanilla. No new scripted helpers remain.
    assert [e.key for e in entries(triggers)] == ['REPLACE:country_is_valid_qing_treaty_partner']
    assert not (ROOT / 'common/scripted_effects/eafp_russo_chinese_effects.txt').exists()
    buttons = read(ROOT / 'common/scripted_buttons/eafp_04_russia_buttons.txt')
    event_text = read(ROOT / 'events/russo_chinese_events.txt')
    assert 'eafp_russo_chinese_' not in buttons + event_text + triggers

    def ownership_guards(text):
        return [e.body(t) for e, t, _ in walk(text) if e.key == 'AND'
                and [c.key for c in entries(e.body(t))] == ['owner', 'OR', 'OR']
                and 'is_split_state' in e.body(t)]

    def canonical_guard(text):
        return text.replace('scope:eafp_qing_treaty_partner', '$DONOR$').replace(
            'scope:donor_scope', '$DONOR$')

    guards = [canonical_guard(g) for g in ownership_guards(buttons + event_text)]
    assert len(guards) == 20 and len({normalized(g) for g in guards}) == 1
    state_guard = guards[0]
    cases = 0
    owners = [Owner('QING'), Owner('THIRD'), Owner('HQ', headquarters=True, overlord='QING'),
              Owner('HQ', headquarters=True, overlord='THIRD'),
              Owner('HQ', headquarters=True, overlord='QING', being_freed=True)]
    for prototype, player, capital, split, region in product(
            owners, (False, True), (False, True), (False, True),
            ('STATE_OUTER_MANCHURIA', 'STATE_AMUR', 'STATE_ALTAI', 'STATE_JETISY', 'STATE_KIRGHIZIA')):
        owner = Owner(**{**vars(prototype), 'player': player})
        state = State(owner, region, capital, split)
        expected_owner = (owner.name == 'QING' and not capital) or (
            owner.headquarters and owner.overlord == 'QING' and not owner.being_freed)
        expected = expected_owner and not player and not (
            split and region in ('STATE_OUTER_MANCHURIA', 'STATE_AMUR'))
        assert state_predicate(state_guard, state) == expected, state
        cases += 1
    for button in entries(buttons):
        b = button.body(buttons)
        available = field(field(b, 'possible'), 'any_country_in_qing_empire')
        drawn = field(field(field(b, 'effect'), 'random_country_in_qing_empire'), 'limit')
        assert normalized(available) == normalized(drawn), button.key
        assert 'country_is_valid_qing_treaty_partner = yes' in drawn
        for e, t, ancestors in walk(field(b, 'effect')):
            if e.key == 'create_incident':
                assert any(p.key == 'show_as_tooltip' for p, _ in ancestors)
        # Each OR alternative remains one conjunctive region check after inlining.
        for e, t, ancestors in walk(b):
            if e.key == 'save_temporary_scope_as' and e.value(t) == 'eafp_qing_treaty_partner':
                assert ancestors[-1][0].key == 'AND'
                region_check = ancestors[-1][0].body(ancestors[-1][1])
                region_fields = entries(region_check)
                assert len(region_fields) == 2 and region_fields[1].key.startswith('s:STATE_')
                assert len(ownership_guards(region_check)) == 1

    def check_settlement(action, infamy, expected, treaty_name):
        # Check the native effects at their execution sites, including their
        # mutually exclusive obligation/infamy and HQ/treaty branches.
        debits = [(e, t, parents) for e, t, parents in walk(action)
                  if e.key == 'set_owes_obligation_to']
        incidents = [(e, t, parents) for e, t, parents in walk(action)
                     if e.key == 'create_incident']
        assert len(debits) == 1 and len(incidents) == (0 if infamy is None else 1)
        e, t, parents = debits[0]
        assert normalized(e.body(t)) == normalized('country = ROOT setting = no')
        assert parents[-1][0].key == 'scope:donor_scope'
        debit_if = parents[-2][0].body(parents[-2][1])
        assert normalized(field(debit_if, 'limit')) == normalized(
            'scope:donor_scope ' + ('?=' if infamy is None else '=') + ' { owes_obligation_to = ROOT }')
        if incidents:
            e, t, parents = incidents[0]
            assert normalized(e.body(t)) == normalized(f'country = scope:donor_scope value = {infamy}')
            assert parents[-1][0].key == 'else_if'
            infamy_branch = parents[-1][0].body(parents[-1][1])
            assert normalized(field(infamy_branch, 'limit')) == normalized(
                'NOT = { scope:donor_scope = { is_subject_of_and_not_being_freed = ROOT } }')
        actual = []
        for e, t, parents in walk(action):
            if e.key != 'create_treaty':
                continue
            treaty = e.body(t)
            state = named(treaty, 'second_country').value(treaty).removesuffix('.owner')
            recipient = named(treaty, 'first_country').value(treaty)
            # The HQ administration returns the land to its own overlord first.
            # The following treaty therefore resolves owner to that overlord.
            siblings = entries(t)
            index = next(i for i, sibling in enumerate(siblings) if sibling.start == e.start)
            assert index > 0 and siblings[index - 1].key == 'if'
            headquarters = siblings[index - 1].body(t)
            assert normalized(field(headquarters, 'limit')) == normalized(
                f'{state}.owner = {{ is_subject_type = subject_type_military_headquarters_china }}')
            direct = field(headquarters, state.removeprefix('scope:'))
            assert normalized(direct) == normalized(f'set_state_owner = {state}.owner.overlord')
            assert named(treaty, 'name').value(treaty) == treaty_name
            assert named(treaty, 'second_country').value(treaty) == state + '.owner'
            assert named(treaty, 'is_draft').value(treaty) == 'no'
            assert normalized(field(treaty, 'binding_period')) == normalized('years = 20')
            assert normalized(field(treaty, 'articles_to_create')) == normalized(
                f'{{ article = state_transfer source_country = {state}.owner '
                f'target_country = {recipient} inputs = {{ {{ state = {state} }} }} }}')
            actual.append((state, recipient))
        assert actual == expected
        assert sum(e.key == 'set_state_owner' for e, _, _ in walk(action)) == len(expected)
        assert action.index('set_owes_obligation_to') < action.index('set_state_owner')
        if incidents:
            assert action.index('create_incident') < action.index('set_state_owner')

    native_effects = {'set_owes_obligation_to', 'create_incident', 'create_treaty', 'set_state_owner'}
    vanilla = read(game / 'events/russo_chinese_events.txt')
    for key in ('russo_chinese.1', 'russo_chinese.2', 'russo_chinese.4'):
        b = named(event_text, key).body(event_text)
        vb = named(vanilla, key).body(vanilla)
        immediate = field(b, 'immediate')
        assert named(field(immediate, 'donor_scope'), 'save_scope_as').value(
            field(immediate, 'donor_scope')) == 'china_scope'
        assert 'random_country =' not in immediate
        assert not native_effects.intersection(e.key for e, _, _ in walk(immediate))
        assert not {'save_scope_value_as', 'remove_variable'}.intersection(e.key for e, _, _ in walk(b))
        assert 'eafp_chuguchak_option_' not in b
        for e, t, _ in walk(immediate):
            if e.key == 'random_scope_state':
                assert len(ownership_guards(field(e.body(t), 'limit'))) == 1
        options = [e.body(b) for e in entries(b) if e.key == 'option']
        original_options = {named(e.body(vb), 'name').value(e.body(vb)): e.body(vb)
                            for e in entries(vb) if e.key == 'option'}
        assert [named(o, 'name').value(o) for o in options] == list(original_options)
        for option in options:
            label = named(option, 'name').value(option)
            original = original_options[label]
            for meta in ('trigger', 'default_option'):
                assert [normalized(e.value(option)) for e in entries(option) if e.key == meta] == [
                    normalized(e.value(original)) for e in entries(original) if e.key == meta], label
            assert not ownership_guards(option)
            assert 'country_is_valid_qing_treaty_partner' not in option
            for e, _, parents in walk(option):
                if e.key in native_effects:
                    assert not any(p.key == 'show_as_tooltip' for p, _ in parents)
            if key == 'russo_chinese.2':
                expected = [('scope:tomsk_scope', 'c:RUS'), ('scope:ili_scope', 'c:RUS')]
                if not label.endswith('.a'):
                    expected.append(('scope:kirghizia_scope', 'scope:kirgiz_scope' if label.endswith('.c') else 'c:RUS'))
                check_settlement(option, 15, expected, 'treaty_name_chuguchak_protocol')
            else:
                state, treaty = ('outer_manchuria_scope', 'beijing') if key.endswith('.1') else ('amur_scope', 'aigun')
                check_settlement(option, None if label == 'russo_chinese.1.a' else 10,
                                 [(f'scope:{state}', 'c:RUS')], f'treaty_name_treaty_of_{treaty}')
                tooltip = field(option, 'custom_tooltip')
                assert named(tooltip, 'text').value(tooltip) == f'treaty_of_{treaty}_tt'
                if key == 'russo_chinese.1':
                    modifier = field(field(option, 'outer_manchuria_scope'), 'add_modifier')
                    expected_modifier = 'modifier_ruler_of_the_east' + ('_navy' if label.endswith('.b') else '')
                    assert named(modifier, 'name').value(modifier) == expected_modifier
                    assert named(modifier, 'days').value(modifier) == 'long_modifier_time'
    for lang in ('english', 'korean', 'simp_chinese'):
        assert 'eafp_russo_chinese_terms_changed:' not in read(
            ROOT / f'localization/{lang}/eafp_china_l_{lang}.yml')
    assert not re.search(r'(?:has|set)_global_variable\s*=\s*rus_', buttons)
    print(f'PASS: {cases} ownership cases across {len(guards)} matching inline conditions; no new scripted helpers; matching button/draw filters; original option layout; option-only settlement; no popup snapshots or ownership rechecks; existing option costs and HQ-overlord treaty transfer.')


def politics_and_treaties(game, ref):
    movements = read(ROOT / 'common/political_movements/zz_eafp_ideological_movements.txt')
    for key in ('movement_meiji_restorationist', 'movement_tokugawa_loyalist'):
        body = named(movements, key).body(movements)
        assert 'has_council_republic_law = yes' in field(body, 'disband_trigger')
        assert 'fold_movement_into_anti_communist_movement_effect = yes' in field(body, 'on_disbanded')
        assert body.count('add = movement_radicalism_suppressed_after_civil_war') == 1
        assert 'days_since_movement_defeated' not in body
    laws = {'law_labour_suffrage', 'law_military_bureaucrats', 'law_communal_administration'}
    ideologies = 0
    for path in (ROOT / 'common/ideologies').glob('*.txt'):
        text, old = read(path), baseline(path.relative_to(ROOT).as_posix(), ref)
        for e in entries(text):
            body = e.body(text)
            original = named(old, e.key.split(':')[-1]).body(old)
            for group in reversed(entries(body)):
                if not group.key.startswith('lawgroup_'):
                    continue
                gb = group.body(body)
                for law in reversed(entries(gb)):
                    if law.key in laws:
                        gb = gb[:law.start] + gb[law.end:]
                body = body[:group.value_start + 1] + gb + body[group.value_end - 1:]
            assert normalized(body) == normalized(original), ('old law stance altered', e.key)
            ideologies += 1
    default = definition(ROOT / 'common/ai_strategies/eafp_default_strategy.txt', 'ai_strategy_default')
    vf = definition(game / 'common/ai_strategies/00_default_strategy.txt', 'ai_strategy_default')
    assert len(entries(default)) == 7
    assert {e.key for e in entries(default)} <= {e.key for e in entries(vf)}
    parties = read(ROOT / 'common/parties/eafp_parties.txt')
    assert len(entries(parties)) == 11
    for p in entries(parties):
        assert p.key.startswith('INJECT:')
        assert {e.key for e in entries(p.body(parties))} <= {'name', 'color'}
    treaty = definition(ROOT / 'common/treaty_articles/eafp_concessions_treaty_articles.txt', 'eafp_grant_concession')
    assert 'can_be_renegotiated' not in normalized(named(treaty, 'flags').value(treaty))
    assert 'any_scope_article_option' in field(treaty, 'can_propose')
    assert 'any_scope_article_option' not in field(treaty, 'can_ratify')
    assert field(treaty, 'on_enforced').strip() == field(treaty, 'on_break').strip() == ''
    assert field(treaty, 'on_entry_into_force').count('eafp_concession_grant_effect') == 1
    assert field(treaty, 'on_withdrawal').count('eafp_concession_return_effect') == 1
    subject = definition(ROOT / 'common/subject_types/eafp_military_headquarters.txt', 'subject_type_military_headquarters_china')
    assert named(subject, 'forced_into_overlord_revolution').value(subject) == 'yes'
    restore = named(subject, 're_establish_war_goal').value(subject)
    war_goal = definition(ROOT / 'common/war_goal_types/eafp_subject_war_goals.txt', restore)
    assert named(war_goal, 'subject_type').value(war_goal) == 'subject_type_military_headquarters_china'
    assert {'validate_subject_relation', 'validate_conflicts_make_subject', 'turns_into_subject'} <= set(normalized(field(war_goal, 'settings')))
    governments = catalogue(ROOT / 'common/government_types')
    assert 'gov_warlord_state' not in governments  # Inherit the full vanilla definition.
    assert 'gov_eafp_russian_warlord_state' not in governments
    vanilla_warlord = definition(game / 'common/government_types/02_presidential_republics.txt',
                                 'gov_warlord_state')
    chinese = definition(ROOT / 'common/government_types/eafp_china_etc.txt', 'gov_chi_warlord_state')
    assert normalized(field(chinese, 'possible')) == normalized('''
        NOT = { has_variable = russian_warlord_country }
        has_law = law_type:law_warlord_government
        OR = {
            is_in_geographic_region = geographic_region_china
            is_in_geographic_region = geographic_region_manchuria_old
        }
    ''')
    for gender in ('male_ruler', 'female_ruler'):
        assert named(vanilla_warlord, gender).value(vanilla_warlord) == '"RULER_TITLE_GENERAL"'
        assert named(chinese, gender).value(chinese) == '"RULER_TITLE_DUJUN"'
    # Renaming the government must also retain the inherited Chinese clique names.
    local_names = catalogue(ROOT / 'common/dynamic_country_names')
    vanilla_names = catalogue(game / 'common/dynamic_country_names')
    for tag, (ve, vt, _) in vanilla_names.items():
        vb = ve.body(vt)
        for variant in entries(vb):
            if 'gov_warlord_state' not in variant.value(vb):
                continue
            expected = variant.body(vb).replace('gov_warlord_state', 'gov_chi_warlord_state')
            name = named(expected, 'name').value(expected)
            le, lt, _ = local_names[tag]
            lb = le.body(lt)
            matches = [e.body(lb) for e in entries(lb) if e.key == 'dynamic_country_name'
                       and named(e.body(lb), 'name').value(e.body(lb)) == name]
            assert len(matches) == 1 and normalized(matches[0]) == normalized(expected), (tag, name)
    for lang in ('english', 'korean', 'simp_chinese'):
        labels = read(ROOT / f'localization/{lang}/jfp_government_l_{lang}.yml')
        for suffix in ('', '_desc'):
            assert f'gov_chi_warlord_state{suffix}:0 "$gov_warlord_state{suffix}$"' in labels
        assert 'gov_eafp_russian_warlord_state' not in labels
    exile = definition(ROOT / 'common/character_interactions/eafp_character_interactions.txt', 'exile_character')
    for required in ('rlit_pushkin_needed_for_golden_age', 'rlit_pushkin_force_duel_effect',
                     'divided_monarchists_ai_active', 'character_matches_divided_monarchists_ai_path',
                     'je_tp_tsar_unshakable_autocracy', 'je_tp_fav_bootlicker'):
        assert required in normalized(exile), required
    print(f'PASS: {ideologies} ideologies preserve old stances; movement suppression once; AI/party inheritance; concession callbacks; HQ restoration; separate warlord titles; exile exceptions.')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--baseline', default='ff358689', help='Pre-P1 commit for preservation checks')
    args = parser.parse_args()
    # Native APIs come from the user's generated 1.15 documentation. Scripted
    # helpers and database fields are checked against the installed vanilla above.
    for filename, keys in {
        'triggers.log': ('is_template_used', 'owns_entire_state_region_uncontested',
                         'is_subject_of_and_not_being_freed', 'any_country_in_qing_empire'),
        'effects.log': ('create_treaty', 'set_state_owner', 'random_country_in_qing_empire',
                        'show_as_tooltip', 'save_scope_value_as'),
    }.items():
        # Some generated prose contains non-UTF-8 bytes; API headings are ASCII.
        raw = (ROOT / 'documentation' / filename).read_bytes()
        documented = {key.decode('ascii') for key in re.findall(rb'^## ([A-Za-z0-9_]+)', raw, re.M)}
        assert not set(keys) - documented, (filename, set(keys) - documented)
    characters(args.game, args.baseline)
    events(args.game, args.baseline)
    russia(args.game)
    politics_and_treaties(args.game, args.baseline)
    print('Runtime still required: popup cancellation/timeouts, HQ treaty execution, government selection, renegotiation, revolution and save/load.')


if __name__ == '__main__':
    main()
