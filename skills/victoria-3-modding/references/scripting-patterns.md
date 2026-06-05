# Victoria 3 Scripting Patterns

## General Jomini Script

- Use `key = value` and nested `{ ... }` blocks.
- Keep braces visually balanced. A missing brace often reports far away from the real mistake.
- Reuse vanilla scope patterns. Common scopes include `ROOT`, `THIS`, `PREV`, `root`, `prev`, `scope:<name>`, `c:TAG`, `s:STATE`, and typed references such as `law_type:law_x`.
- Save scopes before later localization or event use with `save_scope_as = name`.
- Use `hidden_effect` for non-player-facing follow-up effects.
- Prefer named scripted effects/triggers when repeated logic appears more than twice.

## Events

Typical event structure:

```txt
namespace = my_namespace

my_namespace.1 = {
    type = country_event
    placement = ROOT
    title = my_namespace.1.t
    desc = my_namespace.1.d
    flavor = my_namespace.1.f

    duration = 3
    event_image = { video = "some_video_key" }
    icon = "gfx/interface/icons/event_icons/event_newspaper.dds"

    trigger = { ... }
    immediate = { ... }

    option = {
        name = my_namespace.1.a
        default_option = yes
        ...
        ai_chance = { base = 100 }
    }
}
```

Use `trigger_event = { id = namespace.number days = 0 popup = yes }` or `months = { min max }` for delayed flows. Keep event ids unique inside the namespace.

## Journal Entries

Vanilla `common/journal_entries/journal_entries.md` documents the full shape. Common fields:

- `group = journalentrygroup_key`
- `icon = "gfx/interface/icons/..."`
- `is_shown_when_inactive = { ... }`
- `possible = { ... }`
- `immediate = { ... }`
- `complete = { ... }`
- `on_complete = { ... }`
- `fail`, `on_fail`, `invalid`, `on_invalid`
- `status_desc = { first_valid = { triggered_desc = { desc = loc_key trigger = { ... } } } }`
- `scripted_button = scripted_button_key`
- `widget = { gui = "gui/file.gui" name = "widget_name" container = "custom_widget_container_1" }`
- `current_value`, `goal_add_value`, and `progressbar = yes` for tracked goals
- `should_be_pinned_by_default_uninvolved_or_context = yes`
- `weight = number`

Scope notes from the vanilla docs:

- JE root is usually the owning country or no scope.
- `scope:journal_entry` is the journal entry.
- `scope:target` is the target value passed through `add_journal_entry`.
- Scopes saved in `immediate` can be used by JE-triggered events and loc.

When adding a JE, add localization for the key, `_reason`, `_goal` if used, `_status` or dynamic status desc keys, tooltip keys, scripted button text, and event text.

## Scripted Buttons And Progress Bars

Scripted buttons live in `common/scripted_buttons/` and can be listed from a JE with `scripted_button = key`.

```txt
my_button = {
    name = "my_button"
    desc = "my_button_desc"
    visible = { always = yes }
    possible = { ... }
    effect = { ... }
    ai_chance = { base = 0 }
}
```

Scripted progress bars live in `common/scripted_progress_bars/`. Vanilla supports fields such as `name`, `desc`, `second_desc`, `is_inverted`, `start_value`, `min_value`, `max_value`, visual styles like `default = yes`, and `weekly_progress`, `monthly_progress`, or `yearly_progress`.

## Scripted Effects, Triggers, And Values

- Put reusable effects in `common/scripted_effects/`.
- Put reusable boolean checks in `common/scripted_triggers/`.
- Put numeric formulas in `common/script_values/`.
- Search `documentation/effects.log`, `documentation/triggers.log`, and `documentation/data_types_script.txt` when a trigger/effect fails or scope is uncertain.
- Use parameterized scripted effects only after finding a vanilla example with matching syntax.

## Localization

Victoria 3 loc files start with a language header:

```yml
l_korean:
my_key: "Text"
my_key_desc: "Description"
```

Common headers include `l_korean:`, `l_english:`, and `l_simp_chinese:`. Keep every visible key localized in each language the mod supports unless the repo intentionally leaves a fallback. Existing EAFP files use direct keys, `$other_key$` substitutions, Concept links, formatting tags like `#b ... #!`, and escaped newlines `\n\n`.

For events, add:

- `namespace.id.t`
- `namespace.id.d`
- `namespace.id.f` when `flavor` is used
- `namespace.id.a`, `.b`, `.c`, etc. for options

## Countries, History, And Map

- Country tags should use capital letters and numbers only. Vanilla comments warn that lowercase tags can cause civil-war bugs.
- Country definitions live in `common/country_definitions/` and usually define `color`, `country_type`, `tier`, `cultures`, and `capital`.
- Country history lives under `common/history/countries/`; population, buildings, characters, diplomacy, military formations, and movements have their own history subfolders.
- State regions live under `map_data/state_regions/`. When editing state regions, also check history population/buildings and localization for state names.

## GUI And Assets

- JE custom widgets use `widget = { gui = "...gui" name = "..." container = "custom_widget_container_N" }`.
- Scripted GUIs live in `common/scripted_guis/` and visible GUI files live under `gui/`.
- Icon and picture references are usually `gfx/...` paths. Before adding a new asset reference, confirm the file exists and is in a supported format already used nearby.
