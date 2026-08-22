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

## Voice and Register by Text Type

Choose the speaker before choosing the sentence ending. Four voices recur throughout Victoria 3 localization:

- **Editorial narrator:** names and explains the event from outside it.
- **State voice:** expresses what the player-controlled government believes or decides.
- **Diegetic speaker:** a character, crowd, institution, decree, petition, or newspaper speaking inside the world.
- **System voice:** reports conditions, progress, effects, and interface actions without roleplaying a person.

Do not let one voice leak into another. In particular, polite tutorial language does not belong in an event description, and literary court rhetoric does not belong in a progress label.

| Text type | Speaker and stance | Korean default | English default | Simplified Chinese default |
|---|---|---|---|---|
| Event title | Editorial framing; no full narrator | Compact noun phrase, normally no ending or period | Compact title-case noun phrase or short clause | Compact noun phrase, normally no final punctuation |
| Event description | Neutral political or administrative narrator | Written plain style, usually `-했다/-되었다/-하고 있다` | Factual recent-past or present briefing | Concise formal narration with `已/正在/将` as timing requires |
| Flavor vignette | Close third-person narrator inside the scene | Literary `-았다/-었다`; dialogue follows the speaker's social register | Past-tense scene; freer rhythm than the description | Scene narration in past or unfolding aspect; natural dialogue punctuation |
| Flavor quotation/document | The quoted historical or fictional speaker | Preserve the document's `-하노라/-하라/-하옵소서` or other authentic register | Preserve speaker/document cadence | Preserve edict, memorial, newspaper, or colloquial cadence |
| Event option | Player government or ideological reaction | Decisive `-한다/-하자/-하라/-겠다/-리라`, or a short reaction phrase | “We shall…,” “Let us…,” imperative, or terse judgment | Compact commitment such as `必须…`, `让…`, `就…`, or a policy phrase |
| Journal title | Editorial label for a sustained arc | Historical name or noun phrase; no sentence ending | Title-case project, crisis, or metaphor | Historical name or concise project phrase |
| Journal reason | State strategy or close institutional narrator | Plain written `-다`, with `-해야 한다/-할 것이다` for objectives | First-person plural for state projects; close third person for watched crises | `我们必须…` for state projects or close third person for observed subjects |
| Goal | System voice stating success | Condition or outcome fragment: `…할 것`, `…완료`, `…달성` | Infinitive, imperative, or completion condition | Outcome or condition phrase, not conversational prose |
| Status/progress | System voice stating the current state | Present fragment: `…중`, `…임`, `…이상`, `…도달`, or concise `-다` | Present-state label or sentence with the live value foregrounded | Current-state phrase with the live value foregrounded |
| Button label | UI action offered to the player | Verb-object or action noun, normally no period | Imperative verb plus object | Verb-object action phrase |
| Button description | System explanation of the action | Operational `-한다/-할 수 있다/-하게 된다` | Present/future operational prose | Direct explanation of action, eligibility, cost, and result |
| Tooltip/effect text | System result or requirement | UI fragment such as `…함/…됨/…증가/…필요/…이상` | Fragment that completes the surrounding UI, or a direct condition | Compact condition/effect fragment |
| Notification title | Headline-like system narrator | Noun phrase or compact passive headline | Headline/title case | Compact headline |
| Notification description | Neutral report of a completed development | Factual `-했다/-되었다` | Completed-event report, usually recent past or present perfect | Factual completed-event report |

### Event Title Voice

The title is not spoken by the ruler, narrator, or affected population. It is an editorial caption. Prefer a noun phrase, recognized incident, or image. Korean titles should normally not end in `-다`, `-습니다`, or a period. A question or exclamation is exceptional and should frame a real uncertainty or shock, not manufacture excitement.

### Event Description Voice

Use a neutral but situated report. The narrator may understand political causation, but should not sound omniscient, moralizing, or like a modern encyclopedia. Korean descriptions overwhelmingly use written `-다` style in both vanilla and EAFP. Use `-습니다` only when the key is explicitly a report addressed to the ruler/player or when the surrounding feature consistently establishes that formal addressee.

Keep tense tied to event timing:

- completed incident: `-했다/-되었다`, English recent past or present perfect, Chinese `已/刚刚` where natural;
- ongoing crisis: `-하고 있다/-해지고 있다`, English present progressive or present, Chinese `正在/日益`;
- impending consequence: `-할 것이다/-할 수 있다`, English `will/may`, Chinese `将/可能`.

Do not use the option's state voice here. A description reports that the court faces a choice; it does not make the choice.

### Flavor Voice

Flavor has no single universal politeness level because its speaker changes. Declare the mode before drafting:

- A vignette uses a close narrator and usually past-tense `-다` prose in Korean.
- Dialogue uses the character's social position, relationship, region, and emotion. A minister addressing a monarch, two dockworkers, and a revolutionary pamphleteer should not share one register.
- An edict uses authoritative declarative or imperative forms; a petition uses deferential forms; a newspaper uses public report or polemic; a private letter can be intimate.
- An unattributed quotation should sound like a plausible person, not like the omniscient event description placed inside quotation marks.

Never mix neutral narration and courtly honorific speech in the same sentence. Separate quoted speech from narration and let each keep its own register.

#### Online Literary and Situational Research

When internet access is available and the event would benefit from richer historical texture, search for literature or recorded situations related to the event before writing the flavor. Useful sources include:

- novels and serialized fiction written during or about the period;
- diaries, memoirs, letters, petitions, court records, travel accounts, and eyewitness testimony;
- contemporary newspapers, magazines, political pamphlets, songs, and public speeches;
- museum, archive, and scholarly descriptions of how people experienced a comparable incident;
- modern historical fiction portraying a closely analogous social situation.

Use these sources to recover material details, social reactions, rhythms of speech, metaphors, gestures, and plausible scene structure. A scene may deliberately echo or adapt a relevant literary situation when that strengthens the event. Preserve the Victoria 3 event's actual actors, scopes, date, and outcome rather than importing the source's characters or plot wholesale.

Distinguish evidence from inspiration:

- Treat diaries, newspapers, archival documents, and verified contemporary literature as evidence for period detail, while still checking bias and context.
- Treat modern historical novels primarily as inspiration for staging, mood, and interpersonal dynamics, not as proof of a historical fact.
- Cross-check any specific date, office, law, quotation, or factual claim against an authoritative historical source before presenting it as true.
- Search in the relevant original language when practical. If relying on a translation, identify the translator or edition and avoid translating an already translated passage through a third language.

Direct borrowing is acceptable only within the source's legal and editorial limits:

- Public-domain literature and historical documents may be quoted or closely adapted when the wording is verified and suits the event window.
- From copyrighted novels, use only a brief compliant quotation when truly necessary; otherwise paraphrase the underlying situation and write new wording. Do not reproduce a long passage or imitate a living author's distinctive style.
- Do not splice together unattributed lines in a way that makes an invented passage appear to be a real quotation.
- When a flavor closely follows a source, preserve a concise non-player-facing source note in the localization comment if the repository uses such comments, or report the author, work, edition or translator, and link in the task handoff.

The final flavor should still read as native Victoria 3 text. Research supplies the scene's bones; it should not turn the event window into a book excerpt or bibliography.

### Event Option Voice

An option is the player's government speaking through a decision, not the UI politely asking the user for input. Korean options therefore favor decisive plain forms and short reaction phrases, not `-합니다/-하십시오` customer-service language. Across one event, keep the same grammatical frame unless a deliberate contrast is useful:

- commitments: `우리는 …한다`, `…할 것이다`, `…하리라`;
- directives: `…하라`, `…을 지원한다`, `…을 금지한다`;
- collective proposals: `…하자`, `…하도록 하자`;
- reactions: a short noun phrase, aphorism, exclamation, or rhetorical question.

Use `-하옵소서` only if the option is explicitly phrased as advice spoken to a monarch. Use `-십시오` only when an identifiable speaker is respectfully urging another person; it is not the default player-choice voice.

The wording should encode ideology or policy without pretending to list every effect. If one option is coercive and another conciliatory, the verbs must make that contrast audible.

### Journal Reason Voice

The journal reason is a sustained strategic brief. Korean usually uses plain written `-다`, moving from historical diagnosis to `-해야 한다/-할 것이다` when stating the task. English normally uses institutional “we” for a project owned by the country. Use third person when the journal tracks a ruler, movement, epidemic, rebellion, or external country rather than expressing government intent.

Do not address the real-world player as `당신`, “you,” or `你`. Do not use patch-note language such as “the displayed requirements are calculated…” in the narrative voice. If mechanics must appear in the same value, introduce a visibly separate system section after the historical prose.

An EAFP feature may deliberately use courtly Korean throughout a dynastic journal. In that case, decide who is presenting the journal—a memorialist, royal chronicler, or the court itself—and keep that register through the reason text. The title, goal, and status remain UI labels unless they too are explicitly diegetic.

### Goal, Status, Progress, Button, and Tooltip Voice

These are system text, so clarity outranks literary continuity:

- Goal: state what completion looks like, usually without a full polite sentence.
- Status: begin with the changing subject or value and state its current condition.
- Progress bar name: use a noun phrase naming the quantity; the description shows its current value or movement.
- Button label: name the action, not its justification. Avoid punctuation unless the label is intentionally a spoken line.
- Button description: explain what pressing it does, when it can be used, what it costs, and any delay or risk. Use direct present/future prose.
- Tooltip: use the grammar expected by the surrounding interface. Korean tooltips commonly end in `…함`, `…됨`, `…증가`, `…감소`, `…필요`, `…이상`, or another compact condition.

Do not force every fragment into a complete sentence. Conversely, do not use fragmentary tooltip grammar in event descriptions or journal narrative.

### Notification Voice

A notification title behaves like a headline; its description behaves like a compact factual report. It should tell the recipient what happened and to whom, not dramatize the scene or command a response. If action is required, place that instruction in the relevant button or tooltip.

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
- Journal reasons default to plain written `-다`, moving to `-해야 한다` or `-할 것이다` for strategy. Use `-습니다` only when the feature has an explicit formal addressee or an established report-like voice.
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
