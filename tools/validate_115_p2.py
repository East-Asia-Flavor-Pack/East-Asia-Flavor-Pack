"""Validate P2 against the installed 1.15 data; does not simulate gameplay or render UI."""
from argparse import ArgumentParser
from pathlib import Path
import json
import re

from journal_schema import entries, named, normalized
from validate_115_p1 import read, walk

ROOT = Path(__file__).resolve().parents[1]


def field(text, key):
    return named(text, key).body(text)


def scalar(text, key):
    return named(text, key).value(text).strip('"')


def values(text, key):
    return [v.strip('"') for e in entries(text) if e.key == key
            for v in normalized(e.body(text)) if v not in ('{', '}')]


def catalogue(game, folder):
    result = {}
    for base in (game, ROOT):
        for path in sorted((base / folder).glob('*.txt')):
            if base == game and (ROOT / path.relative_to(game)).exists():
                continue
            text = read(path)
            for e in entries(text):
                key = e.key.split(':')[-1]
                body = e.body(text)
                if e.key.startswith('INJECT:'):
                    original = result[key]
                    for change in entries(body):
                        for old in reversed(entries(original)):
                            if old.key == change.key:
                                original = original[:old.start] + original[old.end:]
                    body = original + '\n' + body
                result[key] = body
    return result


def economics(game):
    buildings = catalogue(game, 'common/buildings')
    groups = catalogue(game, 'common/production_method_groups')
    methods = catalogue(game, 'common/production_methods')
    goods = catalogue(game, 'common/goods')
    laws = catalogue(game, 'common/laws')
    techs = catalogue(game, 'common/technology/technologies')
    count = 0
    for path in (ROOT / 'common/history/buildings').glob('*.txt'):
        for e, text, _ in walk(read(path)):
            if e.key != 'create_building':
                continue
            body = e.body(text)
            building = scalar(body, 'building')
            assert building in buildings, (path, building)
            allowed = {pm: g for g in values(buildings[building], 'production_method_groups')
                       for pm in values(groups[g], 'production_methods')}
            used = set()
            for pm in values(body, 'activate_production_methods'):
                assert pm in methods and pm in allowed, (path, building, pm)
                assert allowed[pm] not in used, (path, building, 'duplicate PMG', pm)
                used.add(allowed[pm])
            count += 1
    custom_count = 0
    for path in (ROOT / 'common/production_methods').glob('*.txt'):
        text = read(path)
        for e in entries(text):
            body = e.body(text)
            for key, database in (('unlocking_laws', laws), ('unlocking_technologies', techs)):
                assert not set(values(body, key)) - database.keys(), (path, e.key, key)
            for good in re.findall(r'\bgoods_(?:input|output)_(\w+)_(?:add|mult)\b', body):
                assert good in goods, (path, e.key, good)
            custom_count += 1
    for path in (ROOT / 'common/buildings').glob('*.txt'):
        text = read(path)
        for e in entries(text):
            for group in values(e.body(text), 'production_method_groups'):
                assert group in groups, (path, group)
                assert not set(values(groups[group], 'production_methods')) - methods.keys(), group
    assert 'copper' in goods and 'building_copper_mine' in buildings
    for law in ('law_labour_suffrage', 'law_military_bureaucrats', 'law_communal_administration'):
        assert law in laws
    # Copper and its new PMs are inherited, not copied into the mod a second time.
    assert not any(re.search(r'^(?:REPLACE:|INJECT:)?(?:copper|building_copper_mine)\s*=', read(p), re.M)
                   for folder in ('common/goods', 'common/buildings') for p in (ROOT / folder).glob('*.txt'))
    print(f'PASS: {count} initial buildings/PM memberships; {custom_count} custom PMs; copper and new laws inherited.')


def geography(game):
    states = catalogue(game, 'map_data/state_regions')
    refs = set()
    for folder in ('common', 'events'):
        for path in (ROOT / folder).rglob('*.txt'):
            # Ignore disabled files and comments.
            text = '\n'.join(line.split('#', 1)[0] for line in read(path).splitlines())
            refs.update(re.findall(r'\bs:(STATE_\w+)', text))
    assert not refs - states.keys(), ('unknown state references', sorted(refs - states.keys()))
    partitions = 0
    text = read(ROOT / 'common/history/states/chi_states.txt')
    for e, source, parents in walk(text):
        if e.key != 'create_state':
            continue
        state = next(p.key.removeprefix('s:') for p, _ in reversed(parents) if p.key.startswith('s:'))
        provinces = set(values(e.body(source), 'owned_provinces'))
        assert provinces <= set(values(states[state], 'provinces')), (state, provinces - set(values(states[state], 'provinces')))
        partitions += 1
    for folder in ('map_data', 'gui'):
        overlaps = [p for p in (ROOT / folder).rglob('*') if p.suffix in ('.txt', '.gui')
                    and (game / p.relative_to(ROOT)).exists()]
        assert not overlaps, ('vanilla map/GUI shadowing', overlaps)
    print(f'PASS: {len(refs)} active state references; {partitions} Chinese state partitions; vanilla map/GUI inheritance.')


def presentation(game):
    def asset(relative):
        return next((p for p in (ROOT / relative, game / relative) if p.is_file()), None)
    panel = read(game / 'gui/journal_entry.gui')
    scripted_guis = catalogue(game, 'common/scripted_guis')
    widget_count = 0
    for path in (ROOT / 'common/journal_entries').glob('*.txt'):
        for e, text, _ in walk(read(path)):
            if e.key != 'widget':
                continue
            body = e.body(text)
            gui = asset(scalar(body, 'gui'))
            assert gui, (path, body)
            name = scalar(body, 'name')
            source = read(gui)
            assert re.search(r'\bname\s*=\s*"' + re.escape(name) + r'"', source) or re.search(
                r'\b' + re.escape(name) + r'\s*=\s*{', source), (path, name)
            assert scalar(body, 'container') in panel, (path, body)
            widget_count += 1
    for path in (ROOT / 'gui/journal_entry_widgets').glob('*.gui'):
        for key in re.findall(r"GetScriptedGui\('([^']+)'\)", read(path)):
            assert key in scripted_guis, (path, key)
    for folder in ('common/buildings', 'common/production_methods', 'common/cultures', 'gui/journal_entry_widgets'):
        for path in (ROOT / folder).glob('*'):
            if path.suffix not in ('.txt', '.gui'):
                continue
            for relative in re.findall(r'"(gfx/[^"\[\]]+\.(?:dds|png))"', read(path)):
                assert asset(relative), (path, relative)
    # special_genes is a compound database; compare real gene/template paths.
    def gene_templates(base):
        result = set()
        for path in (base / 'common/genes').glob('*.txt'):
            text = read(path)
            for e, source, parents in walk(text):
                if e.key == 'index':
                    result.add(tuple(p.key for p, _ in parents))
        return result
    local, vanilla = gene_templates(ROOT), gene_templates(game)
    assert not local & vanilla, ('overridden vanilla gene templates', local & vanilla)
    print(f'PASS: {widget_count} journal widget bindings, scripted GUI/assets; {len(local)} custom gene templates without vanilla collisions.')


def release(game):
    assert json.loads(read(ROOT / '.metadata/metadata.json'))['supported_game_version'] == '1.15.*'
    for relative in ('README.md', 'steamdesc.txt'):
        source = read(ROOT / relative)
        assert '1.15' in source and '1.14' not in source, relative
    assert 'documentation/1.14_beta_update_plan.md' not in read(ROOT / 'README.md')
    for relative in ('character_roles/character_roles.md', 'company_types/companies.md',
                     'journal_entries/journal_entries.md', 'political_movements/political_movements.md',
                     'scripted_progress_bars/scripted_progress_bars.md', 'social_classes/readme.md',
                     'social_hierarchies/readme.md', 'treaty_articles/treaty_articles.md'):
        assert read(ROOT / 'common' / relative).split() == read(game / 'common' / relative).split(), relative
    print('PASS: 1.15 release metadata and eight updated vanilla schema documents.')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    args = parser.parse_args()
    economics(args.game)
    geography(args.game)
    presentation(args.game)
    release(args.game)
    print('Runtime pending: new-game prices/employment, winter logistics, portraits/ports/widgets, save/load and DLC-disabled behavior.')


if __name__ == '__main__':
    main()
