# Taiping Journal Design Plan

## Scope

This plan covers two Taiping Heavenly Kingdom (`TPG`) journal entries:

- `je_taiping_house_on_sand`
- `je_taiping_internal_conflict`

Both journals should create a time-attack structure. The player must drive out the Qing before revolutionary fervor collapses, while also preventing internal conflict from consuming the Heavenly Kingdom.

## Core State

- Use `taiping_revolutionary_fervor_progress_bar` on `je_taiping_house_on_sand` as the single source of fervor.
- Use `taiping_internal_conflict` for leadership instability.
- Use scripted progress bars as the visible and monthly-updated source of progress.
- Do not mirror fervor into obsolete country variables.

## Scripted Progress Bars

Add `common/scripted_progress_bars/eafp_taiping_progress_bars.txt`.

### `taiping_revolutionary_fervor_progress_bar`

- `start_value = 100`
- `min_value = 0`
- `max_value = 100`
- `default = yes`
- `monthly_progress` provides all recurring fervor changes and reason localization.

Monthly factors:

- Base war exhaustion: `-2`
- Each unincorporated state: `-1`
- Negative bureaucracy: `-3`
- Negative authority: `-2`
- Legitimacy below 50: `-2`
- Capital occupied: `-5`
- First capture of Beijing: `+15`
- Stable administration, authority, legitimacy, and no unincorporated states: `+2`

### `taiping_internal_conflict_progress_bar`

- `start_value = 10`
- `min_value = 0`
- `max_value = 100`
- `default_bad = yes`
- `monthly_progress` provides all recurring internal conflict changes and reason localization.

Monthly factors:

- Base leadership instability: `+2`
- Negative authority: `+3`
- Legitimacy below 50: `+2`
- Negative bureaucracy: `+2`
- Revolutionary fervor below 40: `+2`
- Authority above 100: `-1`
- Legitimacy above 70: `-1`
- Positive bureaucracy: `-1`

## Journal Wiring

### `je_taiping_house_on_sand`

- Uses `scripted_progress_bar = taiping_revolutionary_fervor_progress_bar`.
- Fails when `scripted_bar_progress(taiping_revolutionary_fervor_progress_bar) <= 0`.
- Completes when Qing no longer exists or China has shattered.
- `on_monthly_pulse` refreshes the fervor combat modifier from the scripted bar and records one-time Beijing capture state.

### `je_taiping_revolution`

- Opens and anchors `je_taiping_house_on_sand`.
- Handles Taiping territorial progress separately from fervor.

### `je_taiping_internal_conflict`

- Uses `scripted_progress_bar = taiping_internal_conflict_progress_bar`.
- Initializes `taiping_internal_conflict` to 10 and syncs the bar.
- Completes when internal conflict reaches 0 and authority, bureaucracy, legitimacy, and incorporated-state requirements are satisfied.
- `on_monthly_pulse` syncs `taiping_internal_conflict` from the scripted bar and fires warning/crisis/collapse events at thresholds.
- On completion, removes internal conflict variables/modifiers so the journal disappears cleanly.

## Modifier Logic

- `je:je_taiping_house_on_sand.scripted_bar_progress:taiping_revolutionary_fervor_progress_bar` controls the multiplier on the existing fervor modifier.
- Above 50 applies `taiping_fervor_high_modifier`.
- Below 50 applies `taiping_fervor_low_modifier`.
- The high multiplier is `(bar - 50) / 50`.
- The low multiplier is `(50 - bar) / 50`.

## Localization

Add name, description, and monthly reason keys for both scripted progress bars in Korean, English, and Simplified Chinese.
