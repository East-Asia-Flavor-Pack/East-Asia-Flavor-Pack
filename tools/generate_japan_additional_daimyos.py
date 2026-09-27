"""Generate researched EAFP han templates, succession and localization.

The JSON roster is the source of historical facts and gameplay choices.
Only marked extension sections in existing files are regenerated.
"""
import argparse
import json
from pathlib import Path
import re

from generate_japanese_culture_patch import find_block

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/data/japan_additional_daimyos.json'


def read(path):
    return path.read_text(encoding='utf-8-sig')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\xef\xbb\xbf' + text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))


def replace_section(text, label, body, anchor=None):
    start, end = f'# EAFP additional han: {label} BEGIN', f'# EAFP additional han: {label} END'
    section = start + '\n' + body.rstrip() + '\n' + end
    pattern = re.escape(start) + r'.*?' + re.escape(end)
    if start in text:
        return re.sub(pattern, lambda _: section, text, flags=re.S)
    assert anchor and anchor in text, label
    return text.replace(anchor, section + '\n' + anchor, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    args = parser.parse_args()
    domains = json.loads(read(DATA))
    existing = {}
    for base in (args.game, ROOT):
        for path in (base / 'localization/simp_chinese').rglob('*.yml'):
            if path.name == 'eafp_japan_additional_daimyos_l_simp_chinese.yml':
                continue
            existing.update(re.findall(r'^\s*([^\s:#]+):\s*(?:\d+\s*)?"([^"\n]*)"', read(path), re.M))
    added = {}

    def name_key(base, chinese, korean):
        candidates = [k for k in existing if re.fullmatch(re.escape(base) + r'(?:_\d+)?', k)]
        for key in candidates:
            if existing[key] == chinese:
                return key
        key, index = base, 2
        while key in existing:
            key, index = f'{base}_{index}', index + 1
        existing[key] = chinese
        added[key] = {'english': base, 'korean': korean, 'simp_chinese': chinese}
        return key

    templates, effects, loc, initial, dispatch, restoration = [], [], [], [], [], []
    for domain in domains:
        han, state, kind = domain['han'], domain['state'], domain['classification']
        family = name_key(domain['family'], domain['family_chinese'], domain['family_korean'])
        for index, person in enumerate(domain['characters']):
            first = name_key(person['name'], person['chinese'], person['korean'])
            year, month, day = map(int, person['birth_date'].split('.'))
            traits = '\n'.join('\t\tadd_trait = ' + trait for trait in person['traits'])
            templates.append(f'''# {domain['family_japanese']}{person['japanese']} / {domain['korean']} / {person['tenure']}
# {person['source']}
{person['template']} = {{
\tfirst_name = {first}
\tlast_name = {family}
\thistorical = yes
\tnoble = yes
\tculture = cu:japanese
\tbirth_date = {person['birth_date']}
\tideology = {person['ideology']}
\tinterest_group = {person['interest_group']}
\thome_region = STATE_{state}
\trole = character_role_magnate
\trole = character_role_politician
\tholding_type = building_manor_house
\ton_created = {{
\t\teafp_japan_register_han_daimyo = {{ STATE = {state} HAN = {han} INDEX = {index} }}
\t\tdesignate_as_{kind}_daimyo = yes
\t}}
\ttrait_generation = {{
{traits}
\t\tif = {{
\t\t\tlimit = {{ game_date < {year + 16}.{month}.{day} }}
\t\t\tadd_trait = trait_child
\t\t}}
\t}}
}}
''')
        initial.append(f'\t\tcreate_character = {{ template = {domain["characters"][0]["template"]} }}')
        dispatch.append(f'''\tif = {{
\t\tlimit = {{ var:daimyo_han_var ?= flag:{han} }}
\t\tJAP_character_generate_{han}_daimyo = yes
\t}}''')
        loc.append(f'''\ttext = {{
\t\ttrigger = {{ var:daimyo_han_var ?= flag:{han} }}
\t\tlocalization_key = domain_{han}
\t}}''')
        restoration.append(f'''\tif = {{
\t\tlimit = {{
\t\t\tthis.state_region ?= s:STATE_{state}
\t\t\towner = {{
\t\t\t\tNOT = {{
\t\t\t\t\tany_scope_character = {{
\t\t\t\t\t\tis_character_alive = yes
\t\t\t\t\t\tvar:daimyo_han_var ?= flag:{han}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t\tJAP_character_generate_{han}_daimyo = yes
\t}}''')
        cases, used = [], []
        for index, person in enumerate(domain['characters'][1:]):
            keyword = 'if' if index == 0 else 'else_if'
            used.append(f'''\t\t\t\t\tAND = {{
\t\t\t\t\t\ts:STATE_{state} = {{ var:eafp_daimyo_chain_id_{han} = {index} }}
\t\t\t\t\t\tis_template_used = {person['template']}
\t\t\t\t\t}}''')
            cases.append(f'''\t\t{keyword} = {{
\t\t\tlimit = {{
\t\t\t\ts:STATE_{state} = {{ var:eafp_daimyo_chain_id_{han} = {index} }}
\t\t\t\tgame_date >= {person['birth_date']}
\t\t\t}}
\t\t\tcreate_character = {{ template = {person['template']} }}
\t\t}}''')
        effects.append(f'''# Character or State scope: matches vanilla succession callers.
JAP_character_generate_{han}_daimyo = {{
\towner = {{ eafp_japan_generate_{han}_daimyo = yes }}
}}

# Country scope. The state-region counter is unique to this han and survives civil wars.
eafp_japan_generate_{han}_daimyo = {{
\tif = {{
\t\tlimit = {{
\t\t\tNOT = {{ has_global_variable = japan_daimyo_abolished }}
\t\t\tany_scope_state = {{ state_region = s:STATE_{state} }}
\t\t}}
\t\ts:STATE_{state} = {{
\t\t\tif = {{
\t\t\t\tlimit = {{ NOT = {{ has_variable = eafp_daimyo_chain_id_{han} }} }}
\t\t\t\tset_variable = {{ name = eafp_daimyo_chain_id_{han} value = 0 }}
\t\t\t}}
\t\t}}
\t\t# Skip used historical people, including dead, retired and foreign characters.
\t\t# Each iteration advances the counter; at most the historical roster's length.
\t\twhile = {{
\t\t\tlimit = {{
\t\t\t\tOR = {{
{chr(10).join(used)}
\t\t\t\t}}
\t\t\t}}
\t\t\ts:STATE_{state} = {{ change_variable = {{ name = eafp_daimyo_chain_id_{han} add = 1 }} }}
\t\t}}
{chr(10).join(cases)}
\t\telse = {{ eafp_japan_generate_random_{han}_daimyo = yes }}
\t}}
}}

# Country scope. An interim random successor does not consume an unborn historical heir.
eafp_japan_generate_random_{han}_daimyo = {{
\tcreate_character = {{
\t\tlast_name = {family}
\t\tnoble = yes
\t\tculture = cu:japanese
\t\trole = character_role_magnate
\t\trole = character_role_politician
\t\tholding_type = building_manor_house
\t\thome_region = STATE_{state}
\t\tinterest_group = {domain['characters'][0]['interest_group']}
\t\ton_created = {{
\t\t\tif = {{
\t\t\t\tlimit = {{ NOT = {{ has_global_variable = japan_daimyo_abolished }} }}
\t\t\t\tset_variable = {{ name = daimyo_var value = s:STATE_{state} }}
\t\t\t\tset_variable = {{ name = daimyo_han_var value = flag:{han} }}
\t\t\t}}
\t\t\tdesignate_as_{kind}_daimyo = yes
\t\t}}
\t}}
}}
''')

    header = '''# Generated from tools/data/japan_additional_daimyos.json.
# Edit the roster and run tools/generate_japan_additional_daimyos.py.

'''
    write(ROOT / 'common/character_templates/eafp_japan_additional_daimyo_templates.txt', header + '\n'.join(templates))
    helpers = '''# Character scope. Historical registration never rewinds a han's succession counter.
eafp_japan_register_han_daimyo = {
\tif = {
\t\tlimit = { NOT = { has_global_variable = japan_daimyo_abolished } }
\t\tset_variable = { name = daimyo_var value = s:STATE_$STATE$ }
\t\tset_variable = { name = daimyo_han_var value = flag:$HAN$ }
\t\ts:STATE_$STATE$ = {
\t\t\tif = {
\t\t\t\tlimit = {
\t\t\t\t\tOR = {
\t\t\t\t\t\tNOT = { has_variable = eafp_daimyo_chain_id_$HAN$ }
\t\t\t\t\t\tvar:eafp_daimyo_chain_id_$HAN$ < $INDEX$
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\tset_variable = { name = eafp_daimyo_chain_id_$HAN$ value = $INDEX$ }
\t\t\t}
\t\t}
\t}
}

'''
    write(ROOT / 'common/scripted_effects/eafp_japan_additional_daimyo_effects.txt', header + helpers + '\n'.join(effects))
    path = ROOT / 'common/scripted_effects/eafp_japan_daimyo_effects.txt'
    text = read(path)
    a, b, body = find_block(text, 'JAP_character_generate_new_daimyo')
    body = replace_section(body, 'succession', '\t#추가: 새 번도 바닐라 사망·해임·쇼군 취임 승계 경로에 연결.\n' + '\n'.join(dispatch), '\towner ?= {')
    text = text[:a] + body + text[b:]
    a, b, body = find_block(text, 'JAP_state_generate_new_daimyo')
    body = replace_section(body, 'restoration', '\t#추가: 한 주의 여러 번을 각각 복구.\n' + '\n'.join(restoration), '\t# je_meiji_restoration_update_daimyos')
    write(path, text[:a] + body + text[b:])
    path = ROOT / 'common/customizable_localization/eafp_japan_daimyo_custom_loc.txt'
    text = read(path)
    # The final brace closes the single custom-localization definition.
    pos = text.rfind('}')
    text = replace_section(text[:pos], 'names', '\t#추가: 새 번의 인물별 번 이름.\n' + '\n'.join(loc), None) if '# EAFP additional han: names BEGIN' in text else text[:pos] + '# EAFP additional han: names BEGIN\n\t#추가: 새 번의 인물별 번 이름.\n' + '\n'.join(loc) + '\n# EAFP additional han: names END\n'
    write(path, text + '}\n')
    path = ROOT / 'common/history/characters/jap - japan.txt'
    text = replace_section(read(path), 'initial', '\t\t#추가: 1836년 재임 중인 새 번의 번주.\n' + '\n'.join(initial), '\t\t# Floating Daimyo')
    write(path, text)
    for language in ('korean', 'english', 'simp_chinese'):
        lines = [f'l_{language}:']
        for domain in domains:
            label = domain['han'].capitalize() if language == 'english' else domain['korean'] if language == 'korean' else domain['japanese'].translate(str.maketrans('賀岡広鳥島', '贺冈广鸟岛'))
            lines.append(f' domain_{domain["han"]}: "{label}"')
        lines += [f' {key}: "{values[language]}"' for key, values in added.items()]
        write(ROOT / f'localization/{language}/eafp_japan_additional_daimyos_l_{language}.yml', '\n'.join(lines) + '\n')
    print(f'Generated {len(domains)} han, {sum(len(d["characters"]) for d in domains)} templates, '
          f'{len(added)} new name keys in three languages; updated lifecycle dispatch and history.')


if __name__ == '__main__':
    main()
