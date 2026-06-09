# Victoria 3 File Map

Use this as a navigation aid. Confirm details against the installed game root for the user's current version.

## Roots

- Game root on this machine: `D:\SteamLibrary\steamapps\common\Victoria 3\game`
- Current mod root observed: `C:\Users\KHG\Documents\GitHub\East-Asia-Flavor-Pack`

## High-Value Game Folders

- `common/`: most data definitions. Important subfolders include `journal_entries`, `scripted_effects`, `scripted_triggers`, `script_values`, `scripted_buttons`, `scripted_progress_bars`, `scripted_guis`, `decisions`, `laws`, `buildings`, `production_methods`, `production_method_groups`, `country_definitions`, `country_formation`, `cultures`, `religions`, `ideologies`, `interest_groups`, `interest_group_traits`, `character_templates`, `character_traits`, `diplomatic_actions`, `treaty_articles`, `modifier_type_definitions`, `static_modifiers`, `on_actions`, `companies`, `power_bloc_*`, and `history`.
- `events/`: country and feature event scripts. Look for `namespace = ...` at the top and numbered event ids.
- `localization/<language>/`: loc files named like `*_l_korean.yml`, `*_l_english.yml`, `*_l_simp_chinese.yml`.
- `localization/<language>/replace/`: localization overrides.
- `gui/`: Clausewitz GUI definitions and journal entry custom widgets.
- `gfx/`: icons, event pictures, portraits, loading screens, models, coat-of-arms assets.
- `map_data/state_regions/`: state region definitions. East Asia examples live in vanilla `11_east_asia.txt`.
- `tools/`: shipped utilities and scripted test examples.

## Useful Vanilla Docs Found In-Game

- `common/journal_entries/journal_entries.md`
- `common/scripted_buttons/scripted_buttons.md`
- `common/scripted_progress_bars/scripted_progress_bars.md`
- `map_data/state_regions/state_regions.md`
- Many `common/<type>/<type>.md` files exist beside their definitions. Search for `*.md` in the specific folder before guessing syntax.

## East Asia Flavor Pack Patterns

- Events use namespaced files such as `events/eafp_kor_events/eafp_korean_reformation_events.txt`, `events/eafp_chi_events/...`, and top-level thematic files.
- Journal entries live in `common/journal_entries/eafp_*.txt`.
- Reusable logic lives in `common/scripted_effects/eafp_*.txt`, `common/scripted_triggers/eafp_*.txt`, `common/script_values/eafp_*.txt`, and related scripted button/progress bar folders.
- Localized text is split by language under `localization/korean`, `localization/english`, and `localization/simp_chinese`.
- `.disable` files are present throughout the repo. Treat them as disabled content, not dead files.
- The repo contains generated lookup logs in `documentation/`; search them before inventing effect, trigger, modifier, or data type names.

## Search Recipes

```powershell
rg -n "je_korean_reformation|korean_reformation_var" common events localization
rg -n "add_journal_entry|has_journal_entry" common events
rg -n "scripted_button =|progressbar = yes|widget =" common\journal_entries common\scripted_buttons common\scripted_progress_bars
rg -n "namespace =|country_event|trigger_event" events
rg -n "has_law_or_variant|add_modifier|set_variable|change_variable" documentation
```
