"""Check the selected 2026-11-07 log fixes; does not replace an engine reload."""
from argparse import ArgumentParser
from pathlib import Path
import re

from journal_schema import entries, named, normalized

ROOT = Path(__file__).resolve().parents[1]
LANGS = ('korean', 'english', 'simp_chinese')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def localization(lang):
    result = {}
    for path in (ROOT / 'localization' / lang).rglob('*.yml'):
        for line in read(path).splitlines():
            match = re.match(r'\s*([^\s:#]+):\d*\s*"(.*)"\s*$', line)
            if match:
                result[match[1]] = match[2]
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True, help='Original error log for the fixes')
    args = parser.parse_args()
    loc = {lang: localization(lang) for lang in LANGS}
    journals = 0
    mirrored = 0
    for path in (ROOT / 'common/journal_entries').glob('*.txt'):
        source = read(path)
        for entry in entries(source):
            body = entry.body(source)
            activation = named(body, 'activation_description').body(body)
            possible = [e for e in entries(body) if e.key == 'possible']
            if possible:
                assert normalized(activation) == normalized(possible[0].body(body)), entry.key
                mirrored += 1
            else:
                assert normalized(activation) == ('always', '=', 'yes'), entry.key
            journals += 1
    assert (journals, mirrored) == (112, 36)
    print('PASS: 112 activation descriptions; 36 match existing eligibility; 76 use always = yes without a tooltip.')

    original = read(args.log)
    checked = set()
    for key, token, relative in re.findall(
            r'Loc key `([^`]+)`: `([^`]+)`[^\n]*missing required quote-escaping[^\n]*file `([^`]+)`', original):
        if not (ROOT / relative).is_file():
            continue  # Vanilla/CMF localization is explicitly outside this task.
        for lang in LANGS:
            text = loc[lang].get(key, '')
            assert all(token not in data for data in re.findall(r'\[[^\[\]]*\]', text)), (lang, key, token)
        checked.add((key, token))
    for lang in LANGS:
        # Verify each dynamic expression, ignoring parentheses inside string arguments.
        for expression in re.findall(r'\[([^\[\]]*)\]', loc[lang]['ijo_information']):
            expression = re.sub(r"'[^']*'", "''", expression)
            depth = 0
            for char in expression:
                depth += (char == '(') - (char == ')')
                assert depth >= 0, (lang, expression)
            assert depth == 0, (lang, expression)
        assert 'japan_invasion.5.t' not in loc[lang]
        assert 'japan_invasion.5.eafp_title' in loc[lang]
    added = []
    for lang in LANGS:
        path = ROOT / 'localization' / lang / f'eafp_115_error_fixes_l_{lang}.yml'
        keys = set(re.findall(r'^ ([\w.]+):', read(path), re.M))
        assert len(keys) == 35
        added.append(keys)
    assert added[0] == added[1] == added[2]
    print(f'PASS: {len(checked)} reported EAFP quote substitutions; 3-language parentheses, title key and 35 added key families.')

    for stem in ('Ahn_Changho', 'Yi_Haung', 'cheoljong', 'jeonbongjun', 'kim_ok_gyun',
                 'min_yeong_hwan', 'seojaepil', 'yoo_giljoon'):
        source = read(ROOT / 'common/dna_data' / f'{stem}.txt')
        assert source.count('gene_asian_east =') == 1, stem
        assert 'gene_asian_east = { "asian_east" 0 "asian_east" 0 }' in source, stem
    source = read(ROOT / 'common/scripted_progress_bars/eafp_bakufu_kaikaku_progress_bars.txt')
    assert 'double_sided_bad' not in source
    for asset in re.findall(r'"(gfx/[^"\n]+\.dds)"', source):
        assert (args.game / asset).is_file() or (ROOT / asset).is_file(), asset
    assert 'gene_asian_east = {' in read(args.game / 'common/genes/01_genes_morph.txt')
    print('PASS: eight DNA morph declarations and native progress-bar assets.')

    for relative in ('common/history/countries/mgl - china.txt', 'common/journal_entries/eafp_chinese_rule.txt'):
        source = read(ROOT / relative)
        assert 'NOT = { has_journal_entry = je_eafp_mgl_restoration_of_the_state }' in source
    assert 'ig:ig_landowners ?= {' in read(ROOT / 'common/scripted_effects/eafp_japan_regional_effects.txt')
    event = named(read(ROOT / 'events/eafp_jap_events/eafp_japan.txt'), 'eafp_japan.2002')
    body = event.body(read(ROOT / 'events/eafp_jap_events/eafp_japan.txt'))
    trigger = named(body, 'trigger').body(body)
    assert 'exists = ruler' in trigger and 'ruler ?=' in trigger
    assert 'eafp_japan_haihan_completed = yes' not in read(ROOT / 'common/journal_entries/eafp_00_meiji_restoration.txt')
    assert 'building_gaudi_gyeong' not in read(ROOT / 'events/eafp_kor_events/eafp_kor_mainline.txt')
    assert 'country_has_state_religion = rel:donghak' not in read(ROOT / 'common/ideologies/eafp_leader_ideologies.txt')
    print('PASS: initialization scope guards, both Mongolian registration guards and removed invalid references.')
    print('Pending: engine reload, portrait/UI review; excluded A1/A4/A6/C errors remain outside these checks.')


if __name__ == '__main__':
    main()
