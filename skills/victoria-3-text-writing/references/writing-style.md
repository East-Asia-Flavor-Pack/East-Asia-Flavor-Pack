# Victoria 3 Writing Style

## The Core Separation

Victoria 3 events read best when each field advances the player's understanding instead of repeating another field:

| Field | Primary job | Typical voice | Common failure |
|---|---|---|---|
| Event title | Frame the moment with a memorable handle | Compact noun phrase or short clause | A sentence-length plot summary |
| Description (`.d`) | State the development and immediate conflict | Clear political or administrative briefing | Encyclopedia background or decorative scene-setting |
| Flavor (`.f`) | Humanize, dramatize, or historicize the development | Vignette, dialogue, quotation, image, document | Restating the description with more adjectives |
| Option | State a response and imply its direction | Decisive player/state voice | Generic “OK,” unexplained joke, or raw effect text |
| Journal title | Name a sustained project or crisis | Thematic title or recognized historical name | A completion condition disguised as a title |
| Journal reason | Explain why this matters and what is at stake | Strategic first-person plural or close institutional voice | A bare checklist, patch note, or implementation disclaimer |
| Goal/status/progress | Explain success conditions or current state | Direct mechanical UI prose | Lore that hides the information the player needs |
| Button description/tooltip | Explain action, cost, risk, cooldown, or result | Direct and operational | Repeating the button label without consequences |

## Event Text

### Title

- Prefer a recognized incident, institution, image, or tension: “The Picked Lock,” “A Remote Posting,” “공허한 유신,” “撬开国门之锁.”
- Use dynamic names only when they materially distinguish the event.
- English normally uses title case. Korean and Simplified Chinese normally use compact noun phrases without English-style capitalization logic.
- A title may be metaphorical when the description immediately makes the subject clear.

### Description

Answer the player's immediate questions in one coherent movement:

1. What changed or was discovered?
2. Which people, institutions, or countries are involved?
3. What tension or decision follows?

One to three sentences is usually enough. Use concrete nouns and active institutions. Historical background belongs here only when the player needs it to understand the choice. The description may use recent past for a completed incident and present tense for an ongoing crisis; do not drift between them without reason.

Do not spend the description explaining exact modifiers already shown below the option. It should make the choice intelligible, not duplicate the effect panel.

### Flavor

Choose one dominant mode:

- **Vignette:** a clerk, soldier, merchant, farmer, courtier, or traveler encounters the change. Use one or two concrete details and a small turn of thought.
- **Dialogue or speech:** let competing assumptions appear in the speaker's words. Keep voices socially and historically plausible.
- **Historical quotation:** use exact wording and attribution only when verified. Put attribution after a line break, commonly `\n\n—Name, Work or Year`.
- **Documentary excerpt:** a decree, petition, memorial, newspaper item, regulation, or treaty clause. Condense aggressively and retain the institutional cadence.
- **Lyric image:** use a repeated object or contrast—old and new ships, smoke over a frontier, a silent throne—to imply the larger transition.

Flavor normally uses one viewpoint. A compact scene is stronger than a survey of everything happening in the country. Paragraph breaks should mark a change in speaker, image, time, or argumentative step.

EAFP sometimes uses long decrees and regulations as flavor. This is appropriate when promulgation is the event, but not the default. Extract the clauses that reveal the reform's scale or controversy; omit exhaustive staffing tables and inventories unless the user explicitly wants a documentary transcription.

### Options

- Make each option understandable before the player reads the effects.
- Use an active verb, policy, judgment, concession, threat, or memorable reaction.
- Let wording foreshadow the branch: suppress, compromise, investigate, fund, delay, recognize, mobilize, or reform.
- Keep the grammatical subject consistent across a set. English commonly uses “We,” “Let us,” an imperative, or an aphoristic reaction. Korean commonly uses a declarative commitment or concise directive. Simplified Chinese commonly uses a compact policy decision.
- Humor is suitable for low-stakes or characterful events, but it should not trivialize famine, massacre, enslavement, or other grave material.
- Do not force option suffixes into a continuous `.a/.b/.c` series. Match the event script exactly.

## Journal Entries

### Title

Use a recognized project or a concise thematic frame. Titles commonly take these forms:

- historical movement or crisis;
- institutional reform;
- territorial or diplomatic objective;
- metaphor that is explained by the reason text;
- series title plus phase, using the punctuation already established nearby.

### Reason

A strong journal reason usually contains two layers:

1. **Narrative layer:** origin of the problem, interested parties, danger or opportunity, and why the state cannot ignore it.
2. **Strategic layer:** what broad result must be achieved and what failure would mean.

Write from the viewpoint appropriate to the journal owner. First-person plural works for state projects; third person works when the journal watches a ruler, faction, epidemic, or external crisis. A historically situated institutional voice is preferable to an omniscient textbook voice.

If the entry has many exact conditions, keep the opening prose readable and move the rules into a separate tooltip, status block, progress description, or clearly labeled final section. Vanilla sometimes combines both in one reason field, but the change of mode is explicit through paragraph breaks, headers, bullets, or tooltippable spans.

Do not imitate placeholder-like EAFP lines such as “the displayed requirements are evaluated...” as narrative style. Such lines are technical notes and should be rewritten as tooltips or paired with an actual historical reason when the UI permits.

### Goal, Status, and Buttons

- Goal text describes the success state or the class of requirements, not the backstory.
- Status text states the current condition and uses dynamic values where useful.
- Progress text identifies the tracked quantity and should show the current value or percentage when the UI supports it.
- Button labels use a verb and object. Button descriptions add rationale, eligibility, cost, cooldown, risk, or expected result.
- Tooltips may be fragmentary because the surrounding UI supplies grammar. Narrative prose should not be fragmentary.

## Language Registers

### English

- Use idiomatic modern English with restrained period color.
- Event descriptions favor lucid political prose. Flavor may be more literary, but avoid strings of abstract adjectives.
- Use title case for event and journal titles; use sentence case for ordinary buttons and tooltips unless nearby keys establish another convention.
- Prefer short Anglo-Saxon verbs for choices: “Open the ports,” “Fund the schools,” “Crush the revolt.”
- Avoid translation artifacts such as repeated “Now it is time to...,” unnecessary “excellent/excellently,” and literal “Let’s wait for time.”
- Use `GetNameNoFormatting` when a name sits inside quotation, possessive grammar, or another formatting span and nearby vanilla usage supports it.

### Korean

- Keep titles compact. Use established Korean historical names rather than retransliterating English labels.
- Event description defaults to clear narrative/reporting prose, usually `-했다/-되었다` or an internally consistent formal equivalent.
- Journal reasons commonly use `-해야 한다`, `-할 것이다`, or an institutional `-습니다` register. Choose one register for the whole feature.
- Reserve courtly forms such as `전하`, `폐하`, `상께서`, `-하옵소서` for an actual memorial, court speaker, or dynastic viewpoint. Do not mix them into neutral UI exposition.
- Attach particles to dynamic expressions using the project's established forms such as `(이)가`, `(을)를`, and `(와)과`, then test both consonant and vowel outcomes where possible.
- Prefer Korean punctuation and natural clause order over English sentence order. Avoid unnecessary spaces before sentences or around punctuation.

### Simplified Chinese

- Use concise titles and standard full-width Chinese punctuation in prose and dialogue.
- Keep dynamic expressions adjacent to the Chinese text unless the expression itself requires spacing.
- Event descriptions favor compact formal narrative; journal reasons can use a state voice such as `我们必须…` when the owner speaks.
- Use `“…”` for dialogue and `《…》` for works where appropriate. Do not mix straight, curly, and corner quotes without a local reason.
- Translate the meaning and institutional register, not Korean or English word order. Verify established Chinese names, offices, reign titles, and transliterations in nearby EAFP and vanilla files.

## Length Calibration

Lengths are soft UI and pacing guidance, not quotas. The local 2026-08-22 corpus showed these median raw character counts:

| Corpus | Title | Description | Flavor | Option | JE reason |
|---|---:|---:|---:|---:|---:|
| Vanilla English | 20 | 247 | 351 | 45 | 285 |
| EAFP English | 26 | 124 | 263 | 30 | 206 |
| Workshop English | 23 | 186 | 363 | 37 | 317 |
| EAFP Korean | 8 | 54 | 124 | 15 | 103 |

These figures include markup and dynamic expressions. Prefer the shortest text that completes the field's job. Long flavor or journal text needs paragraph structure and a reason to occupy the extra space.

## Coherence Review

Before accepting a set, verify:

- the title promises the event actually shown;
- the description presents the decision-driving facts;
- the flavor adds a person, voice, document, or image not already present;
- options represent distinct responses and align with their effects;
- journal reason describes a sustained objective rather than one instantaneous event;
- repeated names, ranks, reign titles, and transliterations match nearby localization;
- no speaker knows facts unavailable from the event's scopes or timing;
- serious historical claims and attributed quotations are verified or clearly fictionalized without false attribution.
