# Local Corpus Notes

This reference records the evidence used to build the writing guidance. It is a snapshot, not a permanent ranking of mods.

## Snapshot and Roots

Survey date: 2026-08-22.

- Vanilla game: `D:\SteamLibrary\steamapps\common\Victoria 3\game`
- Current East Asia Flavor Pack workspace: `C:\Users\KHG\Documents\GitHub\East-Asia-Flavor-Pack`
- Installed workshop content: `D:\SteamLibrary\steamapps\workshop\content\529340`
- Local launcher mods: `C:\Users\KHG\Documents\Paradox Interactive\Victoria 3\mod`

The workshop root contained 71 mod directories. Forty-five contained English localization. All 1,185 discovered `*l_english.yml` files were scanned for key families and length tendencies; mods without English localization were still identified but could not contribute English prose evidence.

## Corpus Scale

The scan parsed single-line quoted localization entries. Counts are useful for calibration but include UI keys that happen to resemble event or journal conventions.

| Corpus | Files | Parsed loc entries | Event titles | Descriptions | Flavor | Options | JE reasons |
|---|---:|---:|---:|---:|---:|---:|---:|
| Vanilla English | 167 | 101,645 | 2,241 | 2,277 | 2,254 | 4,839 | 459 |
| EAFP English | 46 | 8,513 | 581 | 587 | 551 | 942 | 125 |
| EAFP Korean | 47 | 8,637 | 593 | 596 | 562 | 901 | 126 |
| Workshop English | 1,185 | 342,875 | 11,490 | 11,576 | 11,109 | 18,534 | 2,515 |

The Simplified Chinese corpus was inspected comparatively in vanilla and EAFP East Asian features, but was not used for the English length statistics.

## Deep-Read Sources

The full-corpus scan was paired with close reading of script and localization from:

- vanilla `ep2_sakoku`, Meiji, Opium Wars, Taiping, journal, objective, and general event material in English, Korean, and Simplified Chinese;
- EAFP Korean reformation, Korea rework, China, Mongolia, Joseon–Qing War, Ryukyu, JFP event, and replacement localization;
- Better Politics Mod, especially East Asia, ACW, and journals;
- James's Korea Flavor Pack, especially Donghak, reform, Sedo, Imo, and miscellaneous events/journals;
- Mandate of Heaven events and journals;
- Hail, Columbia! events and journal entries;
- Victorian Flavor Mod event and journal collections;
- Morgenröte publishing, workplace, political, trade-good, and country-flavor material;
- other installed mods through the aggregate workshop scan, including their outliers and malformed or placeholder text.

These mods vary greatly in editing quality. Their presence in this list means they informed comparison, not that every line is a model.

## Findings That Change Writing Decisions

### Vanilla is the strongest role model for field separation

Recent vanilla East Asia events consistently use the description for the political fact pattern and the flavor field for a scene, quotation, or recurring image. Options are short enough to scan yet specific enough to imply policy. Use this as the default architecture even when matching an EAFP subject.

### EAFP has a valuable documentary register

EAFP frequently builds flavor from decrees, petitions, regulations, classical arguments, and reform-era polemics. That voice is central to the mod's identity. Its strongest entries select a revealing passage and connect it to the event's conflict. Its weakest entries reproduce exhaustive articles, staffing lists, or inventories that overwhelm the event window. Preserve the register; edit the document.

### EAFP English is often more compressed than vanilla

Median EAFP English descriptions and options were materially shorter than vanilla and the workshop aggregate, while flavor remained substantial. This produces a brisk brief/scene/decision rhythm when the description contains the actual tension. It becomes thin when the description merely announces that something happened.

### Journal reasons span lore and mechanics

Vanilla and major workshop mods often place a narrative opening before mechanical sections separated by paragraphs, headers, bullets, or tooltippable text. EAFP contains both strong historically voiced reasons and technical placeholders such as explanations that displayed conditions are calculated from current state. Use the former as prose models; relocate or clearly label the latter as mechanics.

### Workshop length is not a quality signal

Workshop flavor and journal reasons are longer on average than EAFP, but the corpus includes excellent literary scenes, machine-translated exposition, untranslated text, empty reasons, patch-note language, and enormous rules dumps. Never imitate length or ornate diction without checking whether each sentence serves the field.

### East Asian historical voice needs viewpoint control

The best material distinguishes court memorial, government report, commoner's scene, foreign observer, revolutionary polemic, and neutral UI voice. Generic pseudo-archaic prose blurs those differences. Select the speaker or institution before selecting vocabulary.

### Options reveal quality quickly

Strong option sets encode distinct policies or values and align with downstream effects. Weak sets repeat “Let us,” use generic acceptance, or hide the actual choice behind a joke. Review options together, not one key at a time.

## Source Priority

Use sources according to the decision being made:

1. **Exact terminology and continuity:** same EAFP feature and same language.
2. **EAFP-wide voice:** nearby EAFP material for the same country and era.
3. **UI role and current conventions:** installed vanilla, prioritizing recent DLC/content files and the same script construct.
4. **Alternative treatments and specialist depth:** well-edited workshop features.
5. **Broad frequency or outlier checks:** workshop aggregate.

If EAFP and vanilla disagree on a name, preserve EAFP continuity unless it is clearly an error or the user asks for standardization. If they disagree on whether a field should carry narrative or mechanics, prefer the current vanilla UI role unless the EAFP script requires otherwise.

## Refresh and Search Recipes

Find the live script keys before prose examples:

```powershell
rg -n "title =|desc =|flavor =|status_desc|progress_desc" events common\journal_entries
```

Find related EAFP text across languages:

```powershell
rg -n "namespace_or_journal_key" localization\english localization\korean localization\simp_chinese
```

Find current vanilla treatments of a subject or UI construct:

```powershell
rg -n -i "sakoku|opium|taiping|status_desc" "D:\SteamLibrary\steamapps\common\Victoria 3\game\events" "D:\SteamLibrary\steamapps\common\Victoria 3\game\common\journal_entries" "D:\SteamLibrary\steamapps\common\Victoria 3\game\localization"
```

Find workshop alternatives only after narrowing the concept:

```powershell
rg -n -i "donghak|self-strengthening|journal_key" "D:\SteamLibrary\steamapps\workshop\content\529340" -g "*l_english.yml"
```

When the installed game or workshop corpus changes, treat these counts as stale. Re-run targeted searches and rely on current files rather than the snapshot statistics.
