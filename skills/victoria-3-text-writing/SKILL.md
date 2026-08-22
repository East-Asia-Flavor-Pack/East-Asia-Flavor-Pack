---
name: victoria-3-text-writing
description: Draft, rewrite, translate, or review player-facing Victoria 3 mod localization, especially event titles, descriptions, flavor text, options, journal titles and reasons, status text, goals, buttons, and tooltips for East Asia Flavor Pack. Use when prose quality, historical voice, field-specific style, or English/Korean/Simplified Chinese localization matters; use the general Victoria 3 modding skill for scripting-only work.
---

# Victoria 3 Text Writing

Write localization that is structurally valid, historically grounded, and clearly divided by UI function. Match the current feature's terminology and voice without copying its mistakes.

## Workflow

1. Read the script that consumes the text before drafting.
   - Identify every referenced title, `desc`, `flavor`, option, journal, status, progress, button, and tooltip key.
   - Follow `first_valid` and `triggered_desc` branches. Variants such as `.t1`, `.d2`, `.f.japan`, or nonconsecutive option letters are real only when the script references them.
   - Note the viewpoint, scopes, event outcome, and information the player already sees in effects or tooltips.

2. Read comparable localization in this order:
   - the same EAFP feature and language;
   - nearby EAFP content for the same country, institution, or era;
   - current installed vanilla text at `D:\SteamLibrary\steamapps\common\Victoria 3\game`;
   - strong workshop examples at `D:\SteamLibrary\steamapps\workshop\content\529340`.
   Treat workshop prose as comparative evidence, not as a syntax or quality authority. Preserve established EAFP names, transliterations, concepts, and key conventions unless the user asks to revise them.

3. Assign one job to each field before writing.
   - Event title: identify or frame the moment.
   - Event description: report what happened, where, to whom, and why a decision is needed.
   - Flavor: make the event felt through a scene, voice, image, quotation, or concise document excerpt.
   - Option: express the state's response and foreshadow its direction.
   - Journal title: name the sustained problem or project.
   - Journal reason: establish context, stakes, opposition, and the strategic objective.
   - Goal, status, progress, button description, and tooltip: explain mechanics and current conditions.

4. Draft the authored language first, then localize meaning rather than sentence order.
   - Keep all script expressions and formatting tokens unchanged across languages.
   - Rebuild rhythm, honorifics, particles, and idiom for the target language.
   - If no source language is identified, treat the most complete nearby EAFP language as the semantic source and state that assumption.

5. Review the text in context.
   - Ensure the description and flavor do not retell the same paragraph.
   - Ensure every option is distinguishable before reading its mechanical effects.
   - Ensure journal narrative and mechanical instructions are visually and rhetorically separable.
   - Read dynamic substitutions aloud as if populated; repair grammar around them without changing the expression.

6. Validate keys, tokens, and file format before finishing.
   - Preserve the neighboring `:0`/`:1` or unversioned key convention.
   - Preserve the language header and exact key spelling.
   - Save edited mod text as UTF-8 with BOM and CRLF.
   - Search for every touched key in both script and all supported localization folders.

## References

Read the references required by the task:

- [references/writing-style.md](references/writing-style.md): read whenever authoring or substantially revising events, journal entries, options, or historical flavor.
- [references/localization-syntax.md](references/localization-syntax.md): read whenever editing localization files, dynamic text, conditional variants, or multiple languages.
- [references/corpus-notes.md](references/corpus-notes.md): read when choosing comparison sources, calibrating length, resolving a style dispute, or refreshing the guidance against installed mods.

## Historical Voice and Accuracy

- Use period vocabulary only when it remains clear in the UI. Prefer a controlled nineteenth-century register over theatrical archaism.
- Reflect the institution or speaker's worldview without silently converting it into neutral historical fact.
- Do not fabricate a historical quotation, title, date, office, or attribution. If an exact quotation is unverified, use an unattributed fictional vignette or clearly paraphrase the idea.
- For East Asian court, petition, edict, and classical registers, preserve established EAFP terminology and ranks. Use archaic Korean or literary Chinese selectively and consistently, not as decoration in otherwise modern prose.
- Do not paste a long primary source merely because it is available. Condense it to the part that dramatizes the event unless the document itself is the event's subject.

## Delivery

When asked only to draft text, return complete key families grouped by language and briefly flag any missing script scope or unresolved historical fact. When asked to implement, edit the existing localization files and report which keys were added or revised. Do not alter gameplay effects merely to make prose easier to write.
