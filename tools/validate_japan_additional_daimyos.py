"""Check new han templates and parsed succession tables; does not run Victoria 3."""
import argparse
from datetime import date
import json
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block
from validate_japan_regional_content import structural_check

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return path.read_text(encoding='utf-8-sig')


def block(text, key):
    return re.sub(r'#[^\n]*', '', find_block(text, key)[2])


def day(value):
    return date(*map(int, value.split('.')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    args = parser.parse_args()
    domains = json.loads(read(ROOT / 'tools/data/japan_additional_daimyos.json'))
    template_path = ROOT / 'common/character_templates/eafp_japan_additional_daimyo_templates.txt'
    effect_path = ROOT / 'common/scripted_effects/eafp_japan_additional_daimyo_effects.txt'
    templates, effects = read(template_path), read(effect_path)
    history = read(ROOT / 'common/history/characters/jap - japan.txt')
    routes = read(ROOT / 'common/scripted_effects/eafp_japan_daimyo_effects.txt')
    loc = read(ROOT / 'common/customizable_localization/eafp_japan_daimyo_custom_loc.txt')
    assert len(domains) == 10
    assert sum(len(d['characters']) for d in domains) == 32
    hubs = read(args.game / 'localization/english/dynamic_state_and_hub_names_l_english.yml')
    for han, hub in (('tsu', 'Tsu'), ('fukui', 'Fukui')):
        state = next(d['state'] for d in domains if d['han'] == han)
        assert re.search(r'HUB_NAME_STATE_' + state + r'_wood_japanese:\s*"' + hub + '"', hubs)
    definitions = {}
    for category in ('ideologies', 'character_traits', 'interest_groups', 'character_templates'):
        definitions[category] = {}
        for root in (args.game, ROOT):
            for path in (root / 'common' / category).rglob('*.txt'):
                for key in re.findall(r'^(?:REPLACE:)?(\w+)\s*=\s*\{', read(path), re.M):
                    definitions[category].setdefault(key, []).append(path)
    names = set()
    counters = set()
    cases_by_han = {}
    for domain in domains:
        han, state = domain['han'], domain['state']
        counter = f'eafp_daimyo_chain_id_{han}'
        assert counter not in counters
        counters.add(counter)
        initial = domain['characters'][0]
        assert day(initial['birth_date']) < date(1836, 1, 1)
        start, end = map(int, re.match(r'(\d+)–(\d+)', initial['tenure']).groups())
        assert start <= 1836 <= end
        assert history.count(f'template = {initial["template"]}') == 1
        assert f'localization_key = domain_{han}' in loc
        assert f'var:daimyo_han_var ?= flag:{han}' in block(routes, 'JAP_character_generate_new_daimyo')
        restore = block(routes, 'JAP_state_generate_new_daimyo')
        assert re.search(r'this.state_region \?= s:STATE_' + state + r'\s+owner = \{\s+NOT = \{\s+any_scope_character = \{\s+is_character_alive = yes\s+var:daimyo_han_var \?= flag:' + han, restore)
        for index, person in enumerate(domain['characters']):
            key = person['template']
            assert definitions['character_templates'][key] == [template_path], key
            current = block(templates, key)
            assert f'STATE = {state} HAN = {han} INDEX = {index}' in current
            assert f'birth_date = {person["birth_date"]}' in current
            assert f'home_region = STATE_{state}' in current
            assert f'designate_as_{domain["classification"]}_daimyo = yes' in current
            assert 'noble = yes' in current
            assert 'role = character_role_magnate' in current
            assert 'role = character_role_politician' in current
            assert person['ideology'] in definitions['ideologies']
            assert person['interest_group'] in definitions['interest_groups']
            for trait in re.findall(r'add_trait = (\w+)', current):
                assert trait in definitions['character_traits'], (key, trait)
            names.update(re.findall(r'(?:first|last)_name = (\w+)', current))
            if index:
                assert f'template = {key}' not in history
        generated = block(effects, f'eafp_japan_generate_{han}_daimyo')
        assert 'NOT = { has_global_variable = japan_daimyo_abolished }' in generated
        assert f'any_scope_state = {{ state_region = s:STATE_{state} }}' in generated
        assert f'name = {counter} value = 0' in generated
        assert f'name = {counter} add = 1' in generated
        assert not re.search(r'\bdaimyo_chain_id\b', generated)
        assert not re.search(r'\beafp_japan_generate_' + han + r'_daimyo = yes', generated)
        assert f'owner = {{ eafp_japan_generate_{han}_daimyo = yes }}' in block(effects, f'JAP_character_generate_{han}_daimyo')
        used = block(generated, 'while')
        expected = [(str(i), p['birth_date'], p['template']) for i, p in enumerate(domain['characters'][1:])]
        parsed = re.findall(r'var:' + counter + r' = (\d+) \}\s*game_date >= ([\d.]+)\s*\}\s*create_character = \{ template = (\w+)', generated)
        assert parsed == expected, han
        skipped = re.findall(r'var:' + counter + r' = (\d+) \}\s*is_template_used = (\w+)', used)
        assert skipped == [(i, template) for i, _, template in parsed]
        cases_by_han[han] = parsed
        random = block(effects, f'eafp_japan_generate_random_{han}_daimyo')
        assert f'name = daimyo_var value = s:STATE_{state}' in random
        assert f'name = daimyo_han_var value = flag:{han}' in random
        assert f'designate_as_{domain["classification"]}_daimyo = yes' in random
        assert counter not in random  # Unborn historical successors stay eligible later.
        assert re.search(r'last_name = (\w+)', random)[1] == re.search(r'last_name = (\w+)', block(templates, initial['template']))[1]

    # Evaluate extracted decision tables at date boundaries and with previously used people.
    # This checks the generated table, not the engine's trigger/effect implementation.
    def choose(cases, index, when, used):
        while index < len(cases) and cases[index][2] in used:
            index += 1
        if index < len(cases) and when >= day(cases[index][1]):
            return cases[index][2], index + 1
        return 'random', index

    scenarios = 0
    for cases in cases_by_han.values():
        for index, birthday, key in cases:
            index = int(index)
            born = day(birthday)
            assert choose(cases, index, date.fromordinal(born.toordinal() - 1), set()) == ('random', index)
            assert choose(cases, index, born, set()) == (key, index + 1)
            scenarios += 2
        all_used = {key for _, _, key in cases}
        assert choose(cases, 0, date(1900, 1, 1), all_used) == ('random', len(cases))
        assert choose(cases, len(cases), date(1900, 1, 1), set()) == ('random', len(cases))
        scenarios += 2
    assert len({f'eafp_daimyo_chain_id_{d["han"]}' for d in domains if d['state'] == 'KYUSHU'}) == 3
    names.update(f'domain_{d["han"]}' for d in domains)
    for language in ('english', 'korean', 'simp_chinese'):
        available = set()
        path = ROOT / f'localization/{language}/eafp_japan_additional_daimyos_l_{language}.yml'
        structural_check(path)
        own_keys = re.findall(r'^\s*([^\s:#]+):', read(path), re.M)
        assert len(own_keys) == len(set(own_keys))
        for base in (args.game, ROOT):
            for entry in (base / 'localization' / language).rglob('*.yml'):
                available.update(re.findall(r'^\s*([^\s:#]+):', read(entry), re.M))
        assert names <= available, (language, names - available)
    for path in (template_path, effect_path, ROOT / 'common/history/characters/jap - japan.txt'):
        structural_check(path)
    print(f'PASS: 10 incumbents, 22 historical heirs, 10 random successors, independent counters, '
          f'{scenarios} parsed-table scenarios, lifecycle guards and all names in 3 languages.')


if __name__ == '__main__':
    main()
