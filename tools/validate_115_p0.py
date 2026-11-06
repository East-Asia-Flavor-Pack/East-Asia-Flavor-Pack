"""Validate the 1.15 P0 migration against scripts, docs, and an optional Git base.

python -B tools/validate_115_p0.py --game "D:/SteamLibrary/steamapps/common/Victoria 3/game" --baseline 7770100b
This is a source regression check, not an engine or save-game compatibility test.
"""
import argparse
from collections import Counter
from itertools import product
from pathlib import Path
import re
import subprocess

from journal_schema import entries, named, normalized, outcome
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('complete', 'fail', 'invalid', 'timeout')
STEMS = dict(complete='completion', fail='failure', invalid='invalid', timeout='timeout')
ADJECTIVES = dict(complete='completed', fail='failed', invalid='invalidated', timeout='timeout')
LEGACY = {'complete', 'fail', 'invalid'} | {'on_' + kind for kind in KINDS}
for kind in KINDS:
    LEGACY |= {'custom_' + STEMS[kind] + '_header', 'custom_on_' + STEMS[kind] + '_header',
               'event_outcome_' + ADJECTIVES[kind] + '_desc',
               'event_outcome_' + ADJECTIVES[kind] + '_effect_desc'}


def read(path):
    return (ROOT / path).read_text(encoding='utf-8-sig')


def body(path, key):
    text = read(path)
    return named(text, key).body(text)


def field(text, key):
    return named(text, key).value(text)


def dynasty(text):
    text = re.sub(r'\bhas_variable\s*=\s*(house_tokugawa|house_yamato)\b',
                  r'var:dynasty_var ?= flag:\1', text)
    return text


def compare_baseline(path, current, ref):
    old = subprocess.check_output(['git', 'show', f'{ref}:{path.as_posix()}'],
                                  cwd=ROOT).decode('utf-8-sig')
    old_entries, new_entries = entries(old), entries(current)
    assert [e.key for e in old_entries] == [e.key for e in new_entries], path
    checked = 0
    for old_je, new_je in zip(old_entries, new_entries):
        before, after = old_je.body(old), new_je.body(current)
        key = old_je.key.split(':')[-1]
        original = {e.key: e for e in entries(before)}
        # All unrelated direct fields, including repeated widgets/buttons/pulses,
        # retain their order and payloads. Only dynasty syntax changes within them.
        before_fields = [normalized(dynasty(before[e.start:e.end])) for e in entries(before)
                         if e.key not in LEGACY]
        after_fields = [normalized(after[e.start:e.end]) for e in entries(after) if e.key != 'outcome']
        assert before_fields == after_fields, (key, 'non-outcome fields changed')
        for kind in KINDS:
            if kind not in original and 'on_' + kind not in original:
                continue
            result = outcome(after, kind)
            if kind != 'timeout':
                expected = original[kind].value(before) if kind in original else '{}'
                if normalized(expected) == ('{', '}'):
                    expected = '{ always = no }'
                actual = field(result, 'trigger')
                if kind == 'fail' and 'A fulfilled objective wins' in actual:
                    content = named(result, 'trigger').body(result)
                    gate = entries(content)[-1]
                    assert gate.key == 'hidden_trigger', (key, 'overlap guard')
                    negation = named(gate.body(content), 'NOT').body(gate.body(content))
                    conjunction = named(negation, 'AND').body(negation)
                    completed = outcome(after, 'complete')
                    assert normalized(conjunction) == normalized(named(completed, 'trigger').body(completed)), key
                    actual = '{' + content[:gate.start] + '}'
                if key == 'je_qing_first_opium_war' and kind in ('complete', 'fail'):
                    # The old Qing predicate accidentally required BOTH a treaty
                    # port and investment rights. The truth-table below checks
                    # the corrected mirror of the British OR predicate.
                    pass
                else:
                    assert normalized(dynasty(expected)) == normalized(actual), (key, kind, 'trigger')
            old_effect = original.get('on_' + kind)
            expected = old_effect.value(before) if old_effect else '{}'
            actual = field(result, 'effect')
            if key == 'je_meiji_restoration' and kind in ('fail', 'invalid'):
                actual = actual.replace('remove_variable = restoration_timer_var', '')
            if key == 'je_warlord_china':
                actual = actual.replace('je_warlord_china_cleanup = yes',
                                        'remove_variable = china_warlord_explosion')
            assert normalized(dynasty(expected)) == normalized(actual), (key, kind, 'effect')
            for suffix in ('desc', 'effect_desc'):
                previous = [normalized(dynasty(e.value(before))) for e in entries(before)
                            if e.key == f'event_outcome_{ADJECTIVES[kind]}_{suffix}']
                migrated = [normalized(e.value(result)) for e in entries(result)
                            if e.key == 'event_outcome_' + suffix]
                assert previous == migrated, (key, kind, 'display-only', suffix)
            for old_key, new_key in [('custom_' + STEMS[kind] + '_header', 'header'),
                                     ('custom_on_' + STEMS[kind] + '_header', 'effect_header')]:
                if old_key in original:
                    assert original[old_key].value(before) == field(result, new_key), (key, old_key)
            checked += 1
    return checked


def first_war_matrix():
    """Evaluate the actual result predicates for all relevant Boolean combinations.

    States and treaties here are existence fixtures, not a complete interpreter.
    Unknown predicates fail loudly so the test cannot silently skip new logic.
    """
    path = 'common/journal_entries/eafp_first_opium_war.txt'
    journals = {side: body(path, key) for side, key in
                [('british', 'je_first_opium_war'), ('qing', 'je_qing_first_opium_war')]}

    def evaluate(text, state):
        def check(e):
            key, value = e.key, e.value(text)
            if key in ('AND', 'OR', 'NOT', 'NOR'):
                children = e.body(text)
                values = [evaluate(children[c.start:c.end], state) for c in entries(children)]
                return (all(values) if key == 'AND' else any(values) if key == 'OR'
                        else not any(values))
            if key in ('c:CHI', 'c:GBR', 'scope:target'):
                return evaluate(e.body(text), state)
            if key == 'has_war_with':
                return state['war']
            if key == 'has_law_or_variant':
                assert value == 'law_type:law_free_trade'
                return state['trade']
            if key == 'has_treaty_foreign_investment_rights_with':
                return state['investment']
            if key == 'any_scope_state':
                assert 'is_treaty_port = yes' in value
                return state['port']
            if key == 'any_diplomatic_play':
                assert 'dp_first_opium_war' in value
                return state['play']
            raise AssertionError(('Unknown first-war fixture predicate', key))
        return all(check(e) for e in entries(text))

    for values in product((False, True), repeat=5):
        state = dict(zip(('war', 'trade', 'investment', 'port', 'play'), values))
        results = {side: tuple(evaluate(named(outcome(je, kind), 'trigger').body(outcome(je, kind)), state)
                               for kind in ('complete', 'fail')) for side, je in journals.items()}
        assert results['british'] == results['qing'][::-1], (state, results)
        assert not all(results['british']), (state, results)
        assert not state['war'] or not any(results['british']), (state, results)
    # The British entry alone schedules the four result events; Qing previews them.
    for kind in ('complete', 'fail'):
        result = outcome(journals['qing'], kind)
        effect = named(result, 'effect').body(result)
        assert [e.key for e in entries(effect)] == ['show_as_tooltip']
    print('PASS: 32 first-opium-war result combinations and single event dispatcher.')


def lifecycle():
    japan = body('events/000_eafp_japan_overrides.txt', 'meiji.1')
    assert 'je_meiji_restoration_cleanup = yes' in field(japan, 'after')
    assert 'je_meiji_restoration_cleanup' not in field(japan, 'immediate')
    heavenly = body('events/heavenly_kingdom_events.txt', 'heavenly.4')
    immediate = field(heavenly, 'immediate')
    assert immediate.index('assign_taiping_states = yes') < immediate.index('add_treasury = var:gold_transfer')
    assert 'je_heavenly_kingdom_main_cleanup = yes' in field(heavenly, 'after')
    assert 'add_diplomatic_play_war_support' not in immediate
    pre = outcome(body('common/journal_entries/eafp_00_taiping.txt', 'je_taiping_pre'), 'timeout')
    effect = field(pre, 'effect')
    assert effect.count('add_diplomatic_play_war_support') == 1
    assert effect.index('create_diplomatic_play') < effect.index('add_diplomatic_play_war_support')
    for key in ('opium_wars.3', 'opium_wars.4'):
        event = body('events/opium_wars_events.txt', key)
        assert 'je_opium_obsession_cleanup = yes' in field(event, 'after')
        assert 'remove_variable = opium_wars_unresolved' in event
    for key in ('first_opium_war.152', 'first_opium_war.153', 'first_opium_war.155', 'first_opium_war.251'):
        event = body('events/eafp_chi_events/eafp_first_opium_war_events.txt', key)
        assert 'remove_variable = opium_wars_unresolved' in field(event, 'after')
    hooks = read('common/on_actions/00_code_on_actions_definition.txt')
    registration = named(hooks, 'on_monthly_pulse_character').body(hooks)
    assert [e.key for e in entries(registration)] == ['on_actions']
    for country in ('korea', 'japan', 'china'):
        assert registration.count(country + '_on_monthly_pulse_character') == 1
    pops = read('common/history/pops/99_chi.txt')
    assert not re.search(r'culture\s*=\s*siberian\b', pops)
    assert len(re.findall(r'culture = evenki\s+size = (?:32000|67800|81123)', pops)) == 3
    for root in ('common', 'events'):
        for path in (ROOT / root).rglob('*.txt'):
            code = ' '.join(normalized(path.read_text(encoding='utf-8-sig')))
            assert not re.search(r'(?:has|set|remove)_variable = house_(?:tokugawa|yamato)\b', code), path
    print('PASS: culture IDs, dynasty references, cleanup order, Taiping support, and hook registrations.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--baseline', help='Optional pre-migration Git ref for payload comparison')
    args = parser.parse_args()
    references, totals = set(), Counter()
    for path in sorted((ROOT / 'common/journal_entries').glob('*.txt')):
        structural_check(path)
        text = path.read_text(encoding='utf-8-sig')
        for je in entries(text):
            totals['journals'] += 1
            contents = je.body(text)
            fields = entries(contents)
            assert not LEGACY.intersection(e.key for e in fields), je.key
            results = [e.body(contents) for e in fields if e.key == 'outcome']
            flags = Counter()
            for result in results:
                totals['outcomes'] += 1
                result_fields = {e.key: e.value(result) for e in entries(result)}
                result_flags = normalized(result_fields.get('flags', '{}'))[1:-1]
                flags.update(result_flags)
                assert result_fields['conclusion_desc'], je.key
                references.add(result_fields['conclusion_desc'])
                if 'hidden' not in result_flags:
                    references.update((result_fields['header'], result_fields['effect_header']))
                if 'invalid_outcome' in result_flags:
                    assert 'hidden' in result_flags, je.key
                assert ('trigger' not in result_fields) == ('timeout' in result_flags), je.key
                if 'trigger' in result_fields:
                    assert normalized(result_fields['trigger']) != ('{', '}'), (je.key, 'empty trigger')
                    if 'A fulfilled objective wins' in result_fields['trigger']:
                        totals['explicit_success_precedence'] += 1
                assert 'effect' in result_fields, je.key
            assert flags['timeout'] <= 1 and flags['invalid_outcome'] <= 1, je.key
            has_timeout = any(e.key == 'timeout' and e.value(contents) != '0' for e in fields)
            assert bool(flags['timeout']) == has_timeout, je.key
        if args.baseline:
            totals['baseline_outcomes'] += compare_baseline(path.relative_to(ROOT), text, args.baseline)
    for lang in ('english', 'korean', 'simp_chinese'):
        keys = set()
        for directory in (args.game / 'localization' / lang, ROOT / 'localization' / lang):
            for path in directory.rglob('*.yml'):
                keys.update(re.findall(r'^\s*([^\s:#]+):', path.read_text(encoding='utf-8-sig'), re.M))
        assert not references - keys, (lang, sorted(references - keys))
        path = ROOT / f'localization/{lang}/eafp_journal_outcomes_l_{lang}.yml'
        structural_check(path)
        loc = path.read_text(encoding='utf-8-sig')
        names = re.findall(r'^\s+([^\s:#]+):', loc, re.M)
        assert len(names) == len(set(names))
        assert 'je_boshin_war_concluded' in names and '[' not in loc
    # Every imported cleanup is present in the selected 1.15 game scripts.
    cleanup = (args.game / 'common/scripted_effects/00_victoria_cleanup_scripted_effects.txt').read_text(encoding='utf-8-sig')
    for key in ('je_meiji_restoration_cleanup', 'je_heavenly_kingdom_main_cleanup',
                'je_warlord_china_cleanup', 'je_opium_obsession_cleanup'):
        named(cleanup, key)
    print('PASS:', dict(totals), '; required outcome fields and localization in 3 languages.')
    first_war_matrix()
    lifecycle()


if __name__ == '__main__':
    main()
