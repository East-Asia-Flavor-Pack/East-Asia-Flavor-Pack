"""Static integration checks for Japan's national-JE regional administration.

Run: python tools/validate_japan_regional_content.py
Engine scope and UI checks still require Victoria 3; this is not a game interpreter.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ('TOHOKU', 'KANTO', 'HOKUSHINETSU', 'TOKAI', 'KYOTO', 'KANSAI',
           'CHUGOKU', 'SHIKOKU', 'KYUSHU')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8-sig')


def structural_check(path):
    data = path.read_bytes()
    assert data.startswith(b'\xef\xbb\xbf'), f'Missing BOM: {path}'
    assert not re.search(rb'(?<!\r)\n', data), f'Non-CRLF: {path}'
    text = data.decode('utf-8-sig')
    # Strip comments and quoted literals before checking script delimiters.
    clean = re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*', '', text)
    depth = 0
    for c in clean:
        depth += (c == '{') - (c == '}')
        assert depth >= 0, f'Unexpected closing brace: {path}'
    assert depth == 0, f'Unclosed block: {path}'


def main():
    effects = read('common/scripted_effects/eafp_japan_regional_effects.txt')
    values = read('common/script_values/eafp_japan_regional_values.txt')
    cache = read('common/scripted_effects/eafp_japan_effects.txt')
    je = read('common/journal_entries/eafp_japan.txt')
    gui = read('gui/journal_entry_widgets/eafp_je_bakuhantaisei.gui')
    events = read('events/eafp_jap_events/eafp_japan.txt')
    gates = read('common/scripted_triggers/eafp_japan_regional_triggers.txt')
    boshin = read('events/eafp_jap_events/eafp_boshin_war.txt')
    # Jomini scripted-effect arguments must be scalar tokens, not formula blocks.
    assert not re.search(r'add_bakuhantaisei_state_\w+\s*=\s*\{[^{}]*VALUE\s*=\s*\{', boshin)
    assert boshin.count('save_scope_value_as = { name = eafp_japan_boshin_regional_change') == 63
    assert boshin.count('VALUE = scope:eafp_japan_boshin_regional_change') == 63
    assert boshin.count('clear_saved_scope = eafp_japan_boshin_regional_change') == 63
    for region in REGIONS:
        assert effects.count(f'eafp_japan_refresh_region = {{ STATE = {region} ') == 1
        assert effects.count(f'eafp_japan_monthly_region = {{ STATE = {region} }}') == 1
        for kind in ('loyalty', 'independency'):
            assert f'eafp_japan_{kind}_{region}_monthly = ' in values
            assert f"Var('eafp_japan_{kind}_{region}')" in gui
        for event in ('11', '12'):
            assert f'name = eafp_japan.{event}.{region}' in events
        assert f'owner.eafp_japan_loyalty_{region}_value' in read(
            'common/scripted_progress_bars/eafp_bakuhantaisei_progress_bars.txt')
    assert 'name = cached_daimyo_loyalty value = owner.var:eafp_japan_loyalty_$STATE$' in effects
    assert 'eafp_japan_vanilla_daimyo_cache = yes' in cache
    assert cache.index('eafp_japan_vanilla_daimyo_cache = yes') < cache.index('eafp_japan_refresh_regions = yes')
    assert 'has_variable = eafp_japan_regional_ended' in gates
    assert effects.index('set_variable = eafp_japan_regional_ended') < effects.index('remove_variable = eafp_japan_loyalty_TOHOKU')
    assert je.count('eafp_japan_monthly_regions = yes') == 1
    assert je.count('eafp_japan_end_regions = yes') == 2
    assert 'name = "widget_eafp_japan_regions"' in je and 'name = "widget_eafp_japan_regions"' in gui
    assert gui.count('green_progressbar_horizontal = {') == 9
    assert gui.count('bad_progressbar_horizontal = {') == 9
    assert gui.count('block \"progressbar_size\" { size = { 504 30 } }') == 18
    for region in REGIONS:
        for kind in ('loyalty', 'independency'):
            assert f'tooltip = \"eafp_japan_region_{kind}_{region}_tooltip\"' in gui
    for folder in ('common', 'events'):
        for path in (ROOT / folder).rglob('*.txt'):
            text = path.read_text(encoding='utf-8-sig')
            assert not re.search(r'^\s*je_bakuhantaisei_(?:' + '|'.join(REGIONS) + r')\s*=\s*{', text, re.M), path
    regional_files = [p for directory in ('common', 'events', 'gui') for p in (ROOT/directory).rglob('*')
                     if p.suffix in ('.txt', '.gui') and ('japan_regional' in p.name or p.name in (
                         'eafp_japan_effects.txt', 'eafp_japan.txt', 'eafp_boshin_war.txt',
                         'eafp_bakuhantaisei_progress_bars.txt', 'eafp_je_bakuhantaisei.gui'))]
    for path in regional_files:
        structural_check(path)
        assert not re.search(r'\bgoryo\b|\w+_goryo_\w+', path.read_text(encoding='utf-8-sig'), re.I), path
    # New UI keys must be present once in all three languages.
    keys = set(re.findall(r'(?:text|tooltip) = "(eafp_japan_region\w+)"', gui))
    for lang in ('korean', 'english', 'simp_chinese'):
        loc = read(f'localization/{lang}/eafp_japan_l_{lang}.yml')
        for key in keys:
            assert len(re.findall(r'^\s*' + re.escape(key) + r':', loc, re.M)) == 1, (lang, key)
    print(f'PASS: {len(REGIONS)} regions, one monthly owner, cache contract, lifecycle hooks, '
          f'{len(regional_files)} script/GUI files, {len(keys)} UI keys in three languages, '
          '63 proportional calls with scalar arguments.')


if __name__ == '__main__':
    main()
