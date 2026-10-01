"""Static integration checks for separate daimyo state/han identity.

Run with --game pointing at Victoria 3/game. Does not execute game scripts.
"""
import argparse
import json
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return path.read_text(encoding='utf-8-sig')


def clean(text):
    return re.sub(r'#[^\n]*', '', text)


def block(text, key):
    return clean(find_block(text, key)[2])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    args = parser.parse_args()
    templates = ''.join(read(p) for p in (ROOT / 'common/character_templates').glob('*.txt'))
    vanilla = read(args.game / 'common/character_templates/country_jap.txt')
    effects = read(ROOT / 'common/scripted_effects/eafp_japan_daimyo_effects.txt')
    custom_loc = read(ROOT / 'common/customizable_localization/eafp_japan_daimyo_custom_loc.txt')
    dispatch = block(effects, 'JAP_character_generate_new_daimyo')
    branches = re.findall(
        r'var:daimyo_han_var \?= flag:(\w+)\s*}\s*JAP_character_generate_(\w+)_daimyo = yes',
        dispatch,
    )
    additional = {d['han'] for d in json.loads(read(ROOT / 'tools/data/japan_additional_daimyos.json'))}
    assert len(branches) == 10 + len(additional) and all(han == generator for han, generator in branches)
    assert 'var:daimyo_var' not in dispatch
    names = dict(re.findall(
        r'var:daimyo_han_var \?= flag:(\w+)\s*}\s*localization_key = (\w+)',
        clean(custom_loc),
    ))
    assert set(names) == {han for han, _ in branches}
    assert 'var:daimyo_var' not in clean(custom_loc)

    count = 0
    for key in re.findall(r'^(\w+) = \{', vanilla, re.M):
        original = block(vanilla, key)
        if 'name = daimyo_var' not in original:
            continue
        actual = block(templates, key)
        state = re.search(r'name = daimyo_var value = (s:\w+)', original)[1]
        assert f'name = daimyo_var value = {state}' in actual, key
        han = re.findall(r'name = daimyo_han_var value = flag:(\w+)', actual)
        assert len(han) == 1 and han[0] in names, key
        assert f'localization_key = domain_{han[0]}' in custom_loc, key
        count += 1
    assert count == 40
    for han, _ in branches:
        if han in additional:
            continue  # Their historical roster/counters are checked by the additional-han validator.
        generated = block(effects, f'JAP_character_generate_{han}_daimyo')
        assert generated.count(f'name = daimyo_han_var value = flag:{han}') == 1
        assert generated.count('name = daimyo_var value =') == 1
        for template in re.findall(r'\btemplate = (\w+)', generated):
            assert f'name = daimyo_han_var value = flag:{han}' in block(templates, template)

    cleanup = block(effects, 'character_clear_daimyo_status')
    assert 'remove_variable = daimyo_var' in cleanup
    assert 'remove_variable = daimyo_han_var' in cleanup
    restoration = block(effects, 'JAP_state_generate_new_daimyo')
    for han in names:
        assert f'var:daimyo_han_var ?= flag:{han}' in restoration
    assert 'any_scope_character' not in block(effects, 'japan_replace_missing_daimyo')
    curse = block(effects, 'evaluate_matsumae_curse')
    assert 'var:daimyo_han_var ?= flag:matsumae' in curse

    # Two daimyo sharing a state resolve to separate names and succession branches.
    # The region list must still group them together by the state variable.
    fixture = [('STATE_KYOTO', 'hikone'), ('STATE_KYOTO', 'kaga')]
    routes = dict(branches)
    assert [names[han] for _, han in fixture] == ['domain_hikone', 'domain_kaga']
    assert [routes[han] for _, han in fixture] == ['hikone', 'kaga']
    regional = block(read(ROOT / 'common/scripted_effects/eafp_japan_regional_effects.txt'),
                     'eafp_japan_refresh_region_daimyos')
    assert 'every_scope_character' in regional
    assert 'var:daimyo_var ?= s:STATE_$STATE$' in regional
    assert 'daimyo_han_var' not in regional
    appointment = read(ROOT / 'common/scripted_effects/eafp_japan_effects.txt')
    assert 'var:daimyo_han_var ?= flag:hikone' in appointment
    assert 'var:daimyo_var ?= s:STATE_KYOTO' not in clean(appointment)
    event_path = ROOT / 'events/000_eafp_japan_overrides.txt'
    structural_check(event_path)
    events = clean(read(event_path))
    assert events.count('var:daimyo_han_var ?= flag:hikone') == 2
    assert events.count('var:daimyo_han_var ?= flag:choshu') == 2
    assert events.count('var:daimyo_han_var ?= flag:matsumae') == 1
    assert 'var:daimyo_var ?= s:STATE_CHUGOKU' not in events
    assert 'var:daimyo_var ?= s:STATE_HOKKAIDO' not in events

    # Events use plain IDs, with one mod definition per overridden event.
    assert not re.search(r'^\s*REPLACE:', events, re.M)
    event_keys = re.findall(r'^([\w]+\.\d+)\s*=', events, re.M)
    event_definitions = {}
    for path in (ROOT / 'events').rglob('*.txt'):
        for key in re.findall(r'^(?:REPLACE:)?([\w]+\.\d+)\s*=', read(path), re.M):
            event_definitions.setdefault(key, []).append(path)
    for key in event_keys:
        assert event_definitions[key] == [event_path], (key, event_definitions[key])

    # No competing definitions may override these new REPLACE blocks.
    for category in ('common/character_templates', 'common/scripted_effects',
                     'common/customizable_localization'):
        seen = {}
        for path in (ROOT / category).rglob('*.txt'):
            for key in re.findall(r'^REPLACE:([\w.]+)\s*=', read(path), re.M):
                seen.setdefault(key, []).append(path)
        for path in (ROOT / category).rglob('*daimyo*.txt'):
            structural_check(path)
            for key in re.findall(r'^REPLACE:([\w.]+)\s*=', read(path), re.M):
                assert len(seen[key]) == 1, (key, seen[key])
    print(f'PASS: {count} vanilla historical templates, 10 vanilla generated successors, {len(branches)} distinct han '
          'names/routes, regional grouping, restoration, cleanup and unique overrides.')


if __name__ == '__main__':
    main()
