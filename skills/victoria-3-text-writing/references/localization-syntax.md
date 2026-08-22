# Victoria 3 Localization Syntax for Writers

## File and Entry Shape

Use the language-specific folder, filename suffix, and header:

```yml
l_english:
 my_namespace.1.t: "A New Beginning"
```

```yml
l_korean:
 my_namespace.1.t: "새로운 시작"
```

```yml
l_simp_chinese:
 my_namespace.1.t: "新的开始"
```

Existing files may use `key:0`, `key:1`, or unversioned `key:`. The number is localization version metadata, not part of the key. Preserve the convention of the file being edited; do not normalize a file merely for consistency.

Keep one localization value on one physical line. Encode visible paragraph breaks as `\n\n` and line breaks as `\n`.

## Key Families

### Events

The common family is:

```yml
 my_namespace.1.t: "Title"
 my_namespace.1.d: "Description"
 my_namespace.1.f: "Flavor"
 my_namespace.1.a: "First option"
 my_namespace.1.b: "Second option"
```

This is a convention, not a generator. The event script is authoritative. Conditional blocks may reference keys such as `.ta`, `.t1`, `.d.japan`, `.f2`, or any other valid identifier. Localize every referenced branch and do not create speculative variants.

### Journal Entries

For a journal key `je_example`:

- `je_example` is the title.
- `je_example_reason` is the normal reason text.
- `je_example_status` is the fallback returned when no scripted `status_desc` is defined.
- `je_example_progress` is the fallback returned when no scripted `progress_desc` is defined.
- `_goal`, `_complete`, `_fail`, `_invalid`, and tooltip keys are used only when the script or UI references them.

`status_desc`, `progress_desc`, `complete` custom tooltips, scripted buttons, and widgets may reference arbitrary localization keys. Read the JE definition rather than inferring the complete key set from suffixes.

## Dynamic Localization

Preserve expressions character-for-character unless the script scope itself is being fixed:

```yml
 $other_loc_key$
 [ROOT.GetCountry.GetName]
 [SCOPE.sCountry('target_country').GetName]
 [SCOPE.sCharacter('minister').GetFullName]
 [GetLawType('law_free_trade').GetName]
 [GetStateRegion('STATE_SEOUL').GetName]
 [GetScriptedValue('example_value')|0]
 [Concept('concept_journal_entry', '$concept_journal_entries$')]
 [concept_journal_entry]
```

- `$key$` inserts another localization value.
- Bracket expressions evaluate game data. Do not translate identifiers inside them.
- Formatters after `|` control number, sign, percent, precision, or casing. Preserve them deliberately.
- `GetName` may include game formatting; `GetNameNoFormatting` is useful inside quotations, possessives, or an existing style span. Follow current vanilla or nearby EAFP usage for the same object type.
- A saved scope must exist at the time the text is rendered. If it may be absent, the script needs a conditional localization branch; prose cannot repair an invalid scope.

When translating, compare token sets between languages. Every source token should normally appear exactly once in each translation unless grammar or an intentional omission demands otherwise.

## Formatting and Icons

Common paired spans include:

```text
#bold important text#!
#italic quoted or literary text#!
#v highlighted value#!
#positive_value beneficial text#!
#negative_value harmful text#!
```

The corpus also contains legacy or alias forms such as `#b`, `#BOLD`, color tags, `#lore`, `#tooltippable`, and icons such as `@money!`. Preserve a nearby working pattern rather than inventing a new tag. Every opened formatting span needs a closing `#!` in the correct nesting order.

Use `$EFFECT_LIST_BULLET$` or the bullet convention already established by the relevant vanilla/EAFP UI. Do not put manual mechanics into narrative text when a custom tooltip can display them more clearly.

## Quotes, Paragraphs, and Comments

- Preserve the quote convention of the file. Current files contain escaped quotes (`\"…\"`), doubled edge quotes (`""…""`), and unescaped dialogue inside the outer localization delimiters.
- For new text, prefer the proven convention used in adjacent entries of the same language. Check the result in game when nested quotation marks are complex.
- Use target-language typography inside the value: English curly or straight quotes consistently, Korean quotation marks consistent with nearby text, and Chinese `“…”`/`‘…’` where appropriate.
- Use `\n\n` between prose paragraphs, a quotation and attribution, or narrative and mechanics. Use a single `\n` for list rows or dialogue turns when a full paragraph break is unnecessary.
- An inline `# comment` after the closing value is not player-facing. Preserve useful source or translator notes, but do not expose TODOs as localization.

## Conditional Text

Event and journal scripts often select text through:

```txt
desc = {
    first_valid = {
        triggered_desc = {
            desc = my_namespace.1.d1
            trigger = { ... }
        }
        triggered_desc = {
            desc = my_namespace.1.d2
            trigger = { always = yes }
        }
    }
}
```

The final `always = yes` branch is a fallback. Each branch should describe only facts guaranteed by its trigger. Keep shared wording semantically aligned so that a variant does not accidentally change unrelated facts, tense, or viewpoint.

## Multilingual Consistency

Check parity at three levels:

1. **Keys:** the same live key exists in every language the feature supports.
2. **Tokens:** dynamic expressions, formatting tags, icons, and referenced loc keys are preserved.
3. **Meaning:** stakes, agency, uncertainty, and option intent are the same even when syntax differs.

Do not translate proper names blindly. Search existing localization first:

```powershell
rg -n "Gwanghwamun|광화문|光化门" localization "D:\SteamLibrary\steamapps\common\Victoria 3\game\localization"
```

For Korean dynamic nouns, follow established particle helpers:

```yml
 [SCOPE.sCountry('target').GetName](이)가
 [SCOPE.sCountry('target').GetName](을)를
 [SCOPE.sCountry('target').GetName](와)과
```

Do not add English spaces around Chinese substitutions unless required for a foreign name or UI token.

## Writer-Focused Validation

For a touched feature, use targeted searches rather than scanning only the localization file:

```powershell
rg -n "my_namespace\.1|je_my_feature" events common localization
rg -n "title =|desc =|flavor =|name =|status_desc|progress_desc" events common\journal_entries
rg -n "my_namespace\.1\.(t|d|f|[a-z])" localization
```

Then check:

- each script-referenced key exists;
- no live key exists only in a `.disable` file;
- the correct language header is present;
- outer quotes, formatting spans, and dynamic brackets are balanced;
- options match their effects and `ai_chance` intent;
- conditional variants have a fallback where the script expects one;
- text files are UTF-8 with BOM and CRLF;
- in-game `error.log` shows no missing localization or invalid localization function after runtime testing.
