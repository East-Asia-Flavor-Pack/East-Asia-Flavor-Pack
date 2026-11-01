"""Source-level Boshin journal integration and lifecycle regression checks.

Run: python tools/validate_boshin_international_journal.py
The small trigger evaluator covers these fixtures, not Victoria 3's runtime/UI.
"""
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]
JE = 'common/journal_entries/eafp_boshin_war.txt'
TRIGGERS = 'common/scripted_triggers/eafp_boshin_war_triggers.txt'
EFFECTS = 'common/scripted_effects/eafp_boshin_war_effects.txt'
EVENTS = 'events/000_eafp_japan_overrides.txt'


def read(path):
    return (ROOT / path).read_text(encoding='utf-8-sig')


def block(text, key):
    return find_block(text, key)[2]


def parse(text):
    tokens = iter(re.findall(r'\?=|=|[{}]|[^\s={}?#]+', re.sub(r'#[^\n]*', '', text)))

    def group():
        result = []
        for key in tokens:
            if key == '}':
                return result
            op, value = next(tokens), next(tokens)
            assert op in ('=', '?='), (key, op)
            result.append((key, op, group() if value == '{' else value))
        return result

    return group()


def evaluate(nodes, world, scope=None):
    def check(key, op, value):
        if key in ('AND', 'custom_tooltip'):
            return evaluate(value, world, scope)
        if key == 'OR':
            return any(check(*node) for node in value)
        if key in ('NOT', 'NOR'):
            return not any(check(*node) for node in value)
        if key == 'text':
            return True
        if key in DEFINITIONS:
            return evaluate(DEFINITIONS[key], world, scope) == (value == 'yes')
        if key == 'exists':
            return value.split(':', 1)[1] in world['globals']
        if key == 'has_global_variable':
            return value in world['globals']
        if key.startswith('global_var:'):
            target = world['globals'].get(key.split(':', 1)[1])
            if target is None:
                return op == '?='
            return evaluate(value, world, target) if isinstance(value, list) else target == scope
        if key == 'is_country_alive':
            return (scope in world['alive']) == (value == 'yes')
        if key == 'any_scope_war':
            return any(evaluate(value, world, war) for war in world['wars'] if scope in war['members'])
        if key == 'is_warleader':
            return world['globals'].get(value.split(':', 1)[1]) in scope['leaders']
        if key == 'is_diplomatic_play_enemy_of':
            return {scope, world['globals'].get(value.split(':', 1)[1])} in world['plays']
        raise AssertionError(f'Unsupported fixture predicate: {key}')

    return all(check(*node) for node in nodes)


DEFINITIONS = {key: value for key, _, value in parse(read(TRIGGERS))}


def world(*, sabaku=True, tobaku=True, checked=True, war=False, play=False):
    return {
        'globals': dict(eafp_boshin_active=True, eafp_boshin_sabaku='S', eafp_boshin_tobaku='T',
                        **({'eafp_boshin_checked': True} if checked else {})),
        'alive': {'F', 'U'} | ({'S'} if sabaku else set()) | ({'T'} if tobaku else set()),
        'wars': ([{'leaders': {'S', 'T'}, 'members': {'S', 'T', 'F'}}] if war else []),
        'plays': [{'S', 'T'}] if play else [],
    }


def main():
    je, effects, events = read(JE), read(EFFECTS), read(EVENTS)
    for path in (JE, TRIGGERS, EFFECTS, EVENTS, 'common/journal_entries/eafp_japan.txt'):
        structural_check(ROOT / path)
    assert 'group = je_group_global_international_situations' in je
    assert 'ROOT' not in je and 'c:JAP' not in je
    assert effects.count('add_contextless_journal_entry = je_boshin_war') == 1
    assert 'NOT = { has_global_variable = eafp_boshin_active }' in block(effects, 'eafp_boshin_start')
    for event, sabaku, tobaku in (('ep2_meiji.4', 'scope:tokugawa_scope', 'ROOT'),
                                 ('ep2_meiji.41', 'ROOT', 'scope:imperial_court_scope')):
        body = block(events, event)
        assert f'eafp_boshin_start = {{ SABAKU = {sabaku} TOBAKU = {tobaku} }}' in body
        assert body.count('eafp_boshin_start =') == 1
        assert 'set_variable = eafp_boshin_imperial_support_received' in body
        for support in ('building_port', 'building_trade_center', 'modifier_japan_hiring_bonus',
                        'set_variable = boshin_war_happened', 'remove_bakufu_politician_role = yes'):
            assert support in body, (event, support)
    assert je.count('add_war_war_support =') == 2
    for side in ('sabaku', 'tobaku'):
        assert f'add_war_war_support = {{ target = global_var:eafp_boshin_{side} value = 5 }}' in je
    assert 'trigger_event = { id = boshin_war.9 }' in block(je, 'on_complete')
    for outcome in ('on_complete', 'on_fail', 'on_invalid'):
        assert 'eafp_boshin_cleanup = yes' in block(je, outcome)
    for path in (ROOT / 'common').rglob('*.txt'):
        assert not re.search(r'\bje_boshin_war_(sabaku|tobaku)\b', path.read_text(encoding='utf-8-sig')), path
    assert not re.search(r'\bje_boshin_war_(sabaku|tobaku)\b', events)

    outcomes = {key: parse(block(je, key))[0][2] for key in ('complete', 'fail', 'invalid')}
    cases = [
        ('opening before diplomacy', world(checked=False), (False, False, False)),
        ('diplomatic play', world(play=True), (False, False, False)),
        ('war', world(war=True), (False, False, False)),
        ('shogunate victory', world(tobaku=False), (True, False, False)),
        ('imperial victory', world(sabaku=False), (False, True, False)),
        ('both destroyed', world(sabaku=False, tobaku=False), (False, False, True)),
        ('peace with both surviving', world(), (False, False, True)),
    ]
    for name, state, expected in cases:
        actual = tuple(evaluate(nodes, state) for nodes in outcomes.values())
        assert actual == expected, (name, actual, expected)
    state = world(war=True)
    # An unrelated war involving a Boshin leader must not admit its foreign opponent.
    state['wars'].append({'leaders': {'S', 'U'}, 'members': {'S', 'U'}})
    for country, expected in [('S', True), ('T', True), ('F', True), ('U', False)]:
        assert evaluate(DEFINITIONS['eafp_boshin_country_involved'], state, country) == expected
    state['wars'][0]['members'].remove('F')
    assert not evaluate(DEFINITIONS['eafp_boshin_country_involved'], state, 'F')
    state['globals'].pop('eafp_boshin_tobaku')
    assert not evaluate(DEFINITIONS['eafp_boshin_country_involved'], state, 'U')

    keys = ('je_boshin_war', 'je_boshin_war_reason', 'je_boshin_war_sabaku_victory_header',
            'je_boshin_war_tobaku_victory_header', 'eafp_boshin_sabaku_victory_tt',
            'eafp_boshin_tobaku_victory_tt')
    for lang in ('korean', 'english', 'simp_chinese'):
        path = ROOT / f'localization/{lang}/eafp_japan_l_{lang}.yml'
        structural_check(path)
        loc = path.read_text(encoding='utf-8-sig')
        for key in keys:
            assert len(re.findall(r'^\s*' + key + r':', loc, re.M)) == 1, (lang, key)
        reason = re.search(r'^je_boshin_war_reason:.*$', loc, re.M).group()
        assert 'ROOT.GetCountry' not in reason
    print('PASS: international journal wiring, both opening events, 7 lifecycle scenarios, '
          '6 participation checks, leader-only war support, cleanup and 3 localizations.')


if __name__ == '__main__':
    main()
