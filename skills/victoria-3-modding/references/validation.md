# Victoria 3 Mod Validation

## Before Editing

- Check `git status --short` and avoid overwriting unrelated user changes.
- Find nearby examples in the mod and in the installed game.
- Search for existing identifiers before creating new ones:

```powershell
rg -n "\bnew_key\b" common events localization gui map_data
```

## Script Checks

- Brace balance: inspect the edited block and a few lines above/below. Most Victoria 3 script failures are unbalanced braces, misplaced `limit`, or wrong scope.
- Duplicate keys: search the new top-level key across the mod.
- References: every event, JE, scripted effect, trigger, button, progress bar, GUI widget, modifier, and asset reference should resolve somewhere.
- Scope: if a trigger/effect is used in a new scope, search vanilla usage before assuming it works.
- Disabled files: content in `.disable` files will not load. Do not reference new live content only from disabled files.

## Localization Checks

Run targeted searches for new keys:

```powershell
rg -n "my_event\.1|my_journal_entry|my_tooltip_key" localization
```

Check:

- Loc file has the correct language header.
- Key names match script references exactly.
- Quotes are balanced.
- Long Korean/Chinese strings keep escaped line breaks as `\n\n` when needed.
- `replace/` localization is used only for intentional overrides.

## Runtime Logs

After launching Victoria 3 with the mod, inspect the user log folder:

```text
%USERPROFILE%\Documents\Paradox Interactive\Victoria 3\logs\error.log
%USERPROFILE%\Documents\Paradox Interactive\Victoria 3\logs\game.log
```

Common log categories to chase:

- Unknown trigger/effect or wrong scope.
- Duplicate object id.
- Missing localization key.
- Missing asset path.
- Bad GUI datamodel expression.
- History setup references a missing country, state, culture, religion, building, good, or character template.

## Useful Repository Searches

```powershell
rg -n "has_law_or_variant|add_modifier|set_variable|change_variable" documentation
rg -n "custom_tooltip|first_valid|triggered_desc" common events
rg -n "JournalEntry.Get|ScriptedButton.Get|ExecuteEffect" gui
rg -n "event_image|video =|icon =" events common
```

## Final Review

- Confirm every new player-facing object has localization.
- Confirm all ids use the repo prefix and do not collide with vanilla.
- Confirm event chains have an activation path and terminal path.
- Confirm AI-facing choices have `ai_chance` when player choice should not be random.
- Confirm all touched feature files are live `.txt`, not accidental `.disable`, unless disabling is the task.
