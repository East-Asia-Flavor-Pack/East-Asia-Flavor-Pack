---
name: victoria-3-modding
description: Build, edit, review, or debug Victoria 3 mods using the local Victoria 3 game files, vanilla script examples, generated trigger/effect/modifier documentation, and existing mod repository patterns. Use for Paradox/Jomini scripting tasks involving common/*.txt, events/*.txt, localization/*.yml, gui/*.gui, map_data, gfx assets, journal entries, scripted effects/triggers/buttons/progress bars, countries, history, laws, buildings, companies, diplomatic actions, or East Asia Flavor Pack content.
---

# Victoria 3 Modding

## Core Workflow

1. Identify the mod root and game root before editing.
   - Default game root seen on this machine: `D:\SteamLibrary\steamapps\common\Victoria 3\game`.
   - In this repository, treat the workspace root as a Victoria 3 mod root.
   - If the game root is missing or version-sensitive, ask for the current install path or search only after approval.

2. Read the nearest existing mod pattern first.
   - Prefer files in the same feature area, country, or namespace.
   - Treat `.disable` files as intentionally disabled examples. Do not rename or enable them unless the user asks.
   - Preserve local naming prefixes such as `eafp_` and existing folder conventions.

3. Check vanilla files from the installed game for current syntax.
   - Use `rg --files <game-root>` to locate vanilla examples.
   - Use `rg -n "<key-or-effect>" <game-root>\common <game-root>\events <game-root>\localization` to find canonical usage.
   - Prefer installed-game examples over remembered or older web guidance.

4. Search generated documentation when available.
   - In this repository, `documentation/triggers.log`, `documentation/effects.log`, `documentation/modifiers.log`, `documentation/on_actions.log`, `documentation/event_targets.log`, and `documentation/custom_localization.log` are useful lookup indexes.
   - Use these logs to confirm trigger/effect names, scopes, modifier types, and custom localization functions.

5. Implement the smallest scoped edit.
   - Add new definitions in the matching `common/<type>/` folder.
   - Add events under `events/` with a clear namespace.
   - Add all visible strings to every required `localization/<language>/..._l_<language>.yml` file.
   - Add GUI/assets only when script-side support and localization are already wired.

6. Validate by search and by game logs.
   - Run targeted `rg` checks for duplicate keys, missing localization keys, and unreferenced scripted content.
   - If possible, launch the game and inspect the Victoria 3 `error.log` and `game.log`.

## References

Read only the reference needed for the task:

- `references/file-map.md`: local game/mod folder map and where to look for examples.
- `references/scripting-patterns.md`: common Victoria 3 script patterns for events, journal entries, localization, scripted content, GUI, and history.
- `references/validation.md`: practical checks for syntax, references, localization, and runtime logs.

## Editing Rules

- Preserve Paradox script formatting: tabs/spaces are less important than clear braces, stable keys, and readable nested scopes.
- Do not hand-roll a parser for Jomini script unless the task needs automation; use targeted search and vanilla examples for normal edits.
- Keep identifiers stable once referenced by localization, events, scripted effects, GUI, or history.
- When adding a new feature, include script definitions, event flow, localization, and validation searches in the same pass.
- When unsure about scope, inspect a vanilla file that uses the same trigger/effect before writing.
