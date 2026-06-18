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
   - When creating or editing text files for the mod, save them as UTF-8 with BOM and CRLF line endings.

6. Validate by search and by game logs.
   - Run targeted `rg` checks for duplicate keys, missing localization keys, and unreferenced scripted content.
   - If possible, launch the game and inspect the Victoria 3 `error.log` and `game.log`.

## References

Read only the reference needed for the task:

- `references/file-map.md`: local game/mod folder map and where to look for examples.
- `references/scripting-patterns.md`: common Victoria 3 script patterns for events, journal entries, localization, scripted content, GUI, and history.
- `references/validation.md`: practical checks for syntax, references, localization, and runtime logs.

## Journal Widget GUI

When adding a custom widget to a journal entry, wire the JE script block, the injected GUI object, and any supporting script data together.

```txt
widget = {
    gui = "gui/journal_entry_widgets/my_feature_widgets.gui"
    name = "widget_je_my_feature"
    container = "custom_widget_container_1"
}
```

- Match the JE `name` to an exposed top-level GUI object in the `.gui` file. Two working patterns appear in local/workshop mods:
  - Named wrapper: `flowcontainer = { name = "widget_je_my_feature" ... my_type = {} }`
  - Top-level type instantiation: define `type com_journal_entry_header = widget { name = com_journal_entry_header ... }`, then expose it with `com_journal_entry_header = {}` in an injected `.gui` file.
- A `types ... { type ... }` definition alone is only a reusable type. It must be instantiated by a top-level wrapper or top-level type block whose identifier matches the JE `name`.
- Put reusable shape/layout in `types <namespace> { type <type_name> = widget/container/flowcontainer { ... } }`, then keep the JE-facing wrapper thin. This makes it easy to reuse one visual type for many JEs with different textures, text, or blockoverrides.
- Choose the JE container deliberately: `custom_widget_container_je_icon` replaces the normal JE icon; `custom_widget_container_1` appears above timeout/status; `custom_widget_container_2` appears above scripted buttons; `custom_widget_container_3` appears above scripted progress bars; `custom_widget_container_4` appears above description; `custom_widget_container_5` appears above involved countries; `custom_widget_container_6` appears above progress/completion/failure/timeout; `custom_widget_container_7` appears after that block.
- Use `custom_widget_container_je_icon` for portrait/header/icon replacements. Workshop examples commonly use this for character or illustrated header panels.
- Use `custom_widget_container_3` for panels that sit directly before scripted progress bars: lists, house/faction panels, extra progress explanations, and action controls. Use `custom_widget_container_1` for high-level summaries near the top of the JE body.
- Do not invent a new container name unless you also patch `gui/journal_entry.gui` or an equivalent full JE GUI override with a placeholder like `flowcontainer = { name = "my_custom_container" visible = "[JournalEntry.HasCustomWidget('my_custom_container')]" ... }`.
- If a custom container replaces a vanilla section, hide the vanilla section when `JournalEntry.HasCustomWidget('my_custom_container')` is true. Workshop progress-bar style mods use this to replace the default scripted progress bar list with a custom progress bar container.
- Use `JournalEntry.GetCountry` and `JournalEntry.GetCountry.MakeScope.Var('var_name')` for owner-country data. Use `MakeScope.GetList('list_name')` for list-backed `datamodel` UI and create/update that list before the widget is visible.
- For list items, set the correct `datacontext` inside the item (`Scope.GetCharacter`, `Scope.GetCountry`, `Scope.GetState`, `Scope.GetFlagName`, etc.) before reading object properties.
- For interactive controls, route through `common/scripted_guis/` and call `GetScriptedGui('key').IsValid(...)`, `.ExecuteTooltip(...)`, and `.Execute(...)` with an explicit `GuiScope.SetRoot(...).AddScope(...).End`. Also set `enabled`/`alpha` from `IsValid` so disabled actions are visually clear.
- Use `GetVariableSystem.SetOrToggle`, `Toggle`, or `HasValue` only for UI-local expansion/detail state. Do not use it as game state; persist game state with script variables/effects.
- For dynamic portraits or illustrated headers, prefer stable dimensions (`size`, `minimumsize`, `maximumsize`) and `blockoverride`s rather than letting content resize the JE. Avoid text or icons that can shift surrounding JE sections.
- Validate by searching the JE `name` in both `common/journal_entries` and `gui`, checking all loc keys used by `text`, `tooltip`, and `Localize(...)`, checking all assets in `texture = ...`, and watching `error.log` for missing widget names, bad datacontexts, invalid datamodel expressions, and unknown GUI types.

## Editing Rules

- Preserve Paradox script formatting: tabs/spaces are less important than clear braces, stable keys, and readable nested scopes.
- Do not hand-roll a parser for Jomini script unless the task needs automation; use targeted search and vanilla examples for normal edits.
- Save created or modified mod text files as UTF-8 with BOM and CRLF line endings.
- Keep identifiers stable once referenced by localization, events, scripted effects, GUI, or history.
- When adding a new feature, include script definitions, event flow, localization, and validation searches in the same pass.
- When unsure about scope, inspect a vanilla file that uses the same trigger/effect before writing.
- For scripted progress bars, make the `desc` localization show current progress in the vanilla style rather than a static explanation, for example:
  `Progress: #v [JournalEntry.GetCurrentBarProgress(ScriptedProgressBar.Self)|%]#! ([JournalEntry.GetCurrentBarValue(ScriptedProgressBar.Self)|1]/100)`.
  Use a domain-specific label when appropriate, such as `$my_progress_bar_name$: #v ...#!`.
