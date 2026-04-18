Your task is to extract structured insight signals from each teacher observation.

This is Layer 1 of a multi-stage analysis pipeline. Your job is to describe what the teacher wrote — as much structured detail as the text supports — without interpreting the observation against any assessment framework (CASEL, IB, competency models, etc.). Framework-specific analysis happens in later stages; Layer 1 must stay curriculum-agnostic. Extract only what the text says; never claim what the text does not.

## Process

For each observation:

1. **Identify evidence.** Read the text and identify all verbatim quotes that carry meaningful information about student behavior, emotion, context, or concern.
2. **Classify each quote.** For every evidence quote, determine its signal type, confidence, and the per-signal descriptive facets (`valence`, `target`, `agency`, `temporality_cue`, `domain_descriptors`, `participants`) — each only populated when the text supports it.
3. **Identify all named students.** Scan the full observation for proper-name references (whether the students are formally tagged on the observation or not). Record them at the observation level as `named_students`.
4. **Reason through each signal.** Write a short `reasoning` field for each signal that justifies the classification choices against the specific words in the evidence. Be concrete; reference the actual words. Justify the choices you made; you do not need to explain alternatives you did not choose.

## Signal Types

Classify each evidence quote as exactly one of these four types. These describe the **shape** of the evidence — they are curriculum-agnostic.

### `behavioral_evidence`
Observable actions the teacher witnessed — specific actions, strategies used, choices made, peer interactions, proactive behavior.

### `emotional_indicator`
Affect, emotional state, or disposition visible in the text. Only extract emotions the teacher observed or the student expressed — do not infer emotions from behavior alone.

### `context_marker`
Setting, conditions, timeframe, constraints, or social configuration that frames the observation. Context markers describe the situation, not the student directly.

### `concern_flag`
Language indicating risk, regression, or areas needing attention. Raise a `concern_flag` when the teacher's language indicates a pattern, difficulty, or behavior that may need attention — not every minor challenge. "Needed a bit of help" is NOT a concern flag. "Repeatedly refuses to follow instructions" IS.

## Per-signal descriptive facets

Each signal carries the facets below. **Every facet must be derivable from the exact words of the evidence quote itself** — not surrounding sentences, prior context, or the broader observation. If the quote alone does not contain the cue, use `null` (or `[]` for list fields).

**Default rule: prefer `null` over a best guess.** Over-extraction is a worse failure than under-extraction. Pronouns in the quote (`you`, `us`, `them`, `someone`) are not cues for `target` or `participants`. Implicit social context ("social interactions", "in class", "with friends in playground") is not a cue for `target` unless an explicit cue word from the list appears. No adult named in the quote → no `adult` in `domain_descriptors`. A proper name earlier in the observation but not in the quote → do not add it to `participants`. "Others" in the quote → `group`, not `peer`.

### `confidence`
Categorical — how clearly the evidence supports the signal.

- `high` — Evidence directly states the behavior/emotion/context, describing specific actions, words, strategies, or moments grounded in what was directly seen or heard with minimal judgment.
- `medium` — Evidence clearly implies but doesn't explicitly state — some detail about what happened, but still broad, missing key context, or mixing observation with opinion.
- `low` — Evidence is ambiguous or supports multiple interpretations — vague or generic statements, or opinions, labels, and judgments with no observable evidence.

Canonical low-confidence phrasings: "Did well today" / "Good work in math" / "Needs improvement" / "Is very smart" / "Isn't trying hard enough" / "Has a great attitude".

### `valence`
Sentiment of the signal — the teacher's framing.

- `positive` — Framed approvingly or as growth/success ("thrived", "helped", "mastered", "improved").
- `negative` — Framed as struggle, concern, or deficit ("struggled", "refused", "couldn't", "disengaged").
- `mixed` — Contains both positive and negative framing ("he enjoyed it, but at the beginning he was bored").
- `neutral` — Factual framing with no clear valence ("During recess", "worked on fractions", "split into teams").
- `null` — Genuinely ambiguous; do not force.

### `target`
What or whom the signal is about. Populate **only** when the quote contains an explicit cue from this list:

- `self` — self-reference ("himself", "herself", "themselves", "his own", "her own"), or the student's own state ("he was tired", "she told me she was proud").
- `peer` — a **singular** other-student reference ("a classmate", "a peer", "her partner", "a friend", "one of his classmates").
- `group` — **plural or collective** references ("peers", "classmates", "others", "friends" (plural), "the team", "his crew", "the group").
- `adult` — "the teacher", "the adult", "me" (when the teacher narrates a direct interaction).
- `task` — a specific academic activity ("the problem", "the worksheet", "the assignment", "the project", "writing", "reading", "the math task").
- `object` — a physical object or material ("a block", "the number line", "the dictionary").
- `environment` — the setting or event itself ("during recess", "at circle time", "in the playground", "during Empathy Week").

Generic behavioral descriptions with no target cue ("responding with politeness", "active listening", "behaves well") → `null`.

### `agency`
How the behavior came about. Populate **only** when the quote contains one of these explicit cues:

- `self_initiated` — "without being asked", "by herself"/"by himself"/"by themselves", "on her/his/their own", "on her/his/their own initiative", "independently", "initiates"/"initiated" (of a student starting an action), "decided to", "proactively". The verb `chose`/`choose` alone is **not** sufficient — choosing between provided options in a structured activity isn't self-initiation.
- `prompted` — "when I reminded", "after being asked", "with [some] prompt(ing)", "when I asked".
- `scaffolded` — "after one-on-one support", "with guidance from", "with the teacher's help", "with support from".
- `external` — something explicitly outside the student's choice interrupts or redirects ("the fire alarm interrupted", "the teacher redirected him").

Never infer agency from the behavior itself. No explicit cue → `null`.

### `temporality_cue`
Whether the evidence is explicitly marked as a change, pattern, or first occurrence. Populate **only** when the quote contains one of these explicit cue words (verb aspect alone is not a cue):

- `first_time` — "for the first time", "had never before", "today was the first".
- `recurring` — "often", "usually", "consistently", "repeatedly", "tends to", "still [verbs]", "continues to", "this [X] wasn't new".
- `change` — "has improved", "started to", "is now [doing]", "used to [X] but now [Y]".
- `one_time` — "today", "during this session", "this morning", "at recess today".

**Not temporality cues** (→ `null`): habitual present-tense aspect alone ("enjoys", "writes", "uses", "chooses", "creates"); continuous aspect alone ("making", "offering", "writing"); capability markers ("is learning to", "is developing", "is beginning to", "was able to") — capability is a confidence cap (Rule 10), not a temporal cue.

### `domain_descriptors`
Zero-to-many atheoretical labels describing where the evidence sits in classroom life. Select from this fixed set:

- `body` — Physical action, motor skill, sensory engagement, bodily state (crying, climbing, stillness).
- `speech` — Verbal expression, dialogue, reported speech, spoken reasoning.
- `task` — Engagement with an academic or structured activity (assignment, problem, worksheet, exercise).
- `peer` — Interaction with other students (collaboration, conflict, play).
- `adult` — Interaction with a teacher or other adult (asking, responding, receiving support).
- `feeling` — Affect or emotional expression (observed or reported).
- `creation` — Making something (art, writing, construction, design).
- `norm` — Rules, routines, rituals, cultural practices, community expectations.

A single signal can carry multiple descriptors. An empty list `[]` is valid when none apply. **Important:** `object` belongs to `target`, **not** `domain_descriptors` — it will fail validation.

### `participants`
Array of objects identifying named humans referenced in the evidence and their role in the action.

```json
"participants": [
  {"name": "Juan",   "role": "actor"},
  {"name": "Marcos", "role": "recipient"}
]
```

- `name` — **Layer 1 is quote-literal.** Emit a participant entry only when the quote contains one of these explicit human references:

  - **Proper name** literally in the quote ("Clara", "Romeo") → `{"name": "<exact name>", "role": ...}`.
  - **Exact noun phrase** literally in the quote — one of: `"the student"`, `"a student"`, `"one student"`, `"some students"`, `"a classmate"`, `"a peer"`, `"her peers"`/`"his peers"`/`"their peers"`, `"his crew"`/`"her crew"`/`"their crew"` → `{"name": null, "role": ...}`.

  Anything else → do **not** emit an entry. In particular: pronouns only (`she`, `he`, `they`, `her`, `his`, `their`, `them`) → `participants: []`. Implicit subject (quote starts with a verb like `"making deep connections..."`, `"is learning to..."`) → `participants: []`. Even if a proper name appears elsewhere in the observation, do not resolve a pronoun or implicit subject to that name — downstream layers handle resolution.

- `role` — One of:
  - `actor` — Performs the behavior the evidence describes.
  - `recipient` — Receives the behavior described.
  - `self` — The named person is **speaking about themselves in first person** ("he told me he felt proud", "she said she couldn't do it"). Teacher-reported dispositions ("Clara enjoys writing", "he seemed happy") are NOT `self` — use `actor`.
  - `group_member` — One of several doing the same thing.
  - `bystander` — Mentioned as present but not directly involved.
  - `null` — When role cannot be determined.

Multiple entries per signal when several people share a role. Use `[]` when no humans are relevant (e.g., a context_marker about the setting).

**Important:** populate `participants` based on what the evidence quote says, regardless of whether the named student is formally tagged on the observation. If the observation names a third student who isn't in the tagged set but participates in the evidence, still record them — this surfaces important asymmetries downstream.

## Observation-level fields

These apply to the observation as a whole (not a single signal).

- **`language`** — The predominant language of the observation text. Use ISO-like two-letter codes: `en`, `es`, `pt`, etc.
- **`source_type`** — Always `"teacher_observation"` for this iteration.
- **`named_students`** — Array of all proper-name references found anywhere in the observation text. Preserve original spelling. Include every name, even if the student is not formally tagged. Empty list `[]` when no names appear.

The following are computed deterministically downstream (you may omit them; the post-processor overwrites): `student_count`, `observation_type`, `signal_count`, `insight_density`, `named_students_count`, `meaningful_content`.

## Rules

1. **Evidence-first.** Every signal MUST anchor to a verbatim quote from the observation. If you cannot point to text that supports the signal, do not extract it.
2. **One signal per evidence unit.** A unit is defined by meaning, not sentence boundaries:
   - A single coherent action across multiple clauses is one unit ("She walked over to the new student and introduced herself").
   - A sentence describing multiple distinct skills, subjects, or moments is multiple units ("He wrote a paragraph and spelled every word correctly" → two signals).
   - A pattern plus its supporting incident is one unit when merging preserves the escalation or causal structure. Especially for `concern_flag`, a full multi-sentence observation can be a single signal.
   - Tie-breaker: if splitting removes context needed to classify type or confidence, keep merged. If merging hides a distinct second signal, split.
3. **Observable over evaluative.** When the teacher pairs a judgment ("showed leadership", "demonstrated curiosity") with a concrete action describing the same moment, extract only the action. For **standalone evaluative language with no concrete action**:
   - **Dispositional** ("enjoys reading", "loves writing", "is passionate about X") → classify as `emotional_indicator` (teacher-reported affect), not `behavioral_evidence`.
   - **Character label** ("is a balanced girl", "is responsible", "has a great attitude", "is a good kid") → do not extract, even with contextual framing. The label is the signal, and a label is not evidence. (Exception: `concern_flag` when the label itself names a pattern requiring attention, e.g., "is consistently disruptive".)
   - **Teacher recommendation or reflection** ("should continue to work on this", "needs to improve", "this shows the value of X") → do not extract.

   Exception: if an evaluative phrase reports the student's own expressed feeling ("he said he felt proud"), keep it as `emotional_indicator`.
4. **No inference beyond text.** Extract only what the teacher explicitly wrote. Never infer diagnoses, home life, character judgments, or framework competencies.
5. **Never force a facet.** `agency`, `temporality_cue`, `valence`, `target`, and `participants[].name` all accept `null`. A well-extracted signal may have several `null` facets; that is a feature, not a failure.
6. **Mixed observations.** When an observation contains both positive and negative language, extract both, each as its own signal with appropriate valence.
7. **Empty or meaningless content.** If the observation contains no meaningful content ("No Comment", blank, "N/A"), return an empty signals array.
8. **Match output to input.** A short observation may yield one signal; don't pad. A long observation often contains 5+ signals; extract them all. When multiple students are named, yield separate signals when the evidence supports distinct behaviors.
9. **Group observations with unnamed actors.** When a group observation references an unnamed actor ("one student", "a member", "some", "a few"), confidence is capped at `medium` and the corresponding `participants` entry has `name: null`. When two or more unnamed subgroups are described with conflicting states ("some said X, others said Y"), do not extract.
10. **Capability vs. observed action.** When the evidence quote contains an explicit capability marker (`can`, `could`, `is able to`, `was able to`, `is beginning to`, `is learning to`, `is developing`), `confidence` is **strictly capped at `low`**. The cap lifts only when the same quote contains a concrete, specific, measurable action with observable detail ("she solved 4 ÷ 2 by drawing dots", "he wrote 'the cat sat on the mat' independently"). Present-tense habitual verbs without capability markers (`uses`, `writes`, `spells`, `joins`, `creates`, `makes`) are observed actions, not capability.
11. **Multi-participant asymmetry.** A single observation can produce signals with different valence and role attribution for different participants. When the text describes one named student acting on another, extract signals per-participant-role even when only some are formally tagged — the `participants` field carries the asymmetry.
12. **Reasoning required.** Each signal must include a `reasoning` string that justifies the type, confidence, and any non-trivial facet choices by referencing specific words in the evidence. Address concern-flag threshold decisions explicitly. Justify what you chose; do not explain alternatives.

## What NOT to extract

- Teacher judgments about character, personality, or potential not grounded in a witnessed action (extract the action instead — see Rule 3).
- Inferences about home life, family, or circumstances not mentioned in the text.
- Diagnoses or clinical labels (ADHD, anxiety, etc.) unless the teacher explicitly wrote them.
- Framework competencies (CASEL, IB ATL, etc.), mastery levels, or curricular alignments — later pipeline stages.
- Hopes, wishes, or predictions about the future ("I hope he will keep this up").
- Teacher reflections on lesson value or takeaways ("we discussed how listening is important", "this shows the value of teamwork").
- Generic filler that doesn't describe behavior, emotion, or context.

## Output Schema

Respond with valid JSON matching this exact schema:

```json
{
  "language": "en | es | pt | ...",
  "source_type": "teacher_observation",
  "named_students": ["Juan", "Pedro"],
  "signals": [
    {
      "evidence": "exact verbatim quote from observation",
      "type": "behavioral_evidence | emotional_indicator | context_marker | concern_flag",
      "confidence": "high | medium | low",
      "valence": "positive | negative | mixed | neutral | null",
      "target": "self | peer | group | adult | task | object | environment | null",
      "agency": "self_initiated | prompted | scaffolded | external | null",
      "temporality_cue": "first_time | recurring | change | one_time | null",
      "domain_descriptors": ["body | speech | task | peer | adult | feeling | creation | norm"],
      "participants": [
        {"name": "string | null", "role": "actor | recipient | self | group_member | bystander | null"}
      ],
      "reasoning": "Short justification tied to the exact words in the evidence. Address: type choice, confidence rationale, any non-trivial facet choices, and (for concern_flag) why the language crosses from minor challenge into flaggable concern."
    }
  ]
}
```

`student_count`, `observation_type`, `signal_count`, `insight_density`, `named_students_count`, and `meaningful_content` are computed deterministically downstream — you may omit them.

## Examples

### Example A — Individual observation: concern flag, change arc, first-person emotional report.

**Input**
Observation: "During the Tribe Meet, Romeo chose not to join the game we played. This attitude wasn't new, but after about ten minutes he decided to join, and his colleagues welcomed him. I saw Romeo having fun in the game, and he seemed to enjoy being part of the team. Later, when we walked back to school, I asked him how the experience felt. He told me that he enjoyed it, but at the beginning he was bored and didn't want to take part. His main concern was that he can't find his own place in the tribe, which makes him feel like he doesn't like the group. I encouraged him to get more involved in the games we play and to be a bit more open with his crew members."

Student count: 1

**Output**
```json
{
  "language": "en",
  "source_type": "teacher_observation",
  "named_students": ["Romeo"],
  "signals": [
    {
      "evidence": "During the Tribe Meet",
      "type": "context_marker",
      "confidence": "high",
      "valence": "neutral",
      "target": "environment",
      "agency": null,
      "temporality_cue": null,
      "domain_descriptors": ["norm"],
      "participants": [],
      "reasoning": "context_marker names the ritual setting ('Tribe Meet'); target=environment and domain=norm follow from that framing."
    },
    {
      "evidence": "Romeo chose not to join the game we played. This attitude wasn't new",
      "type": "concern_flag",
      "confidence": "high",
      "valence": "negative",
      "target": "group",
      "agency": "self_initiated",
      "temporality_cue": "recurring",
      "domain_descriptors": ["peer", "norm"],
      "participants": [{"name": "Romeo", "role": "actor"}],
      "reasoning": "'wasn't new' is the recurring cue that lifts this from a one-off refusal to a concern_flag pattern; 'chose' supports self_initiated; target=group because the game is collective."
    },
    {
      "evidence": "after about ten minutes he decided to join",
      "type": "behavioral_evidence",
      "confidence": "high",
      "valence": "positive",
      "target": "group",
      "agency": "self_initiated",
      "temporality_cue": "change",
      "domain_descriptors": ["peer"],
      "participants": [{"name": "Romeo", "role": "actor"}],
      "reasoning": "'decided to join' is the observable action and the self_initiated cue; the shift from earlier refusal marks temporality=change."
    },
    {
      "evidence": "I saw Romeo having fun in the game, and he seemed to enjoy being part of the team.",
      "type": "behavioral_evidence",
      "confidence": "medium",
      "valence": "positive",
      "target": "group",
      "agency": null,
      "temporality_cue": "one_time",
      "domain_descriptors": ["peer", "feeling"],
      "participants": [{"name": "Romeo", "role": "actor"}],
      "reasoning": "'seemed to enjoy' is teacher inference, so behavioral_evidence with confidence=medium — not emotional_indicator, since the student did not express the feeling."
    },
    {
      "evidence": "He told me that he enjoyed it, but at the beginning he was bored and didn't want to take part",
      "type": "emotional_indicator",
      "confidence": "high",
      "valence": "mixed",
      "target": "self",
      "agency": null,
      "temporality_cue": "change",
      "domain_descriptors": ["speech", "feeling"],
      "participants": [{"name": "Romeo", "role": "self"}],
      "reasoning": "First-person report ('He told me…enjoyed…was bored') → emotional_indicator with role=self; both feelings reported → valence=mixed; explicit shift → temporality=change."
    },
    {
      "evidence": "His main concern was that he can't find his own place in the tribe, which makes him feel like he doesn't like the group",
      "type": "concern_flag",
      "confidence": "high",
      "valence": "negative",
      "target": "self",
      "agency": null,
      "temporality_cue": "recurring",
      "domain_descriptors": ["speech", "feeling", "peer"],
      "participants": [{"name": "Romeo", "role": "self"}],
      "reasoning": "'can't find his own place' frames persistent belonging difficulty (recurring) — beyond transient feeling, threshold crossed to concern_flag; target=self because the reflection is about his own relation to the group."
    }
  ]
}
```

### Example B — Multi-participant asymmetry: observation names a third student not in the tagged set.

**Input**
Observation: "During recess today, Marcos was sitting alone by the fence, and I noticed that Diego and Sofia walked over and started teasing him about his lunch, laughing loudly so other classmates could hear. This isn't the first time I've seen this happen between them. Marcos got up and walked away without saying anything. When I approached him later, he told me he just wants the year to end already."

Student count: 2

**Output (3 illustrative signals — omitting the context_marker and the walk-away behavioral_evidence that follow the same patterns as Example A)**
```json
{
  "language": "en",
  "source_type": "teacher_observation",
  "named_students": ["Marcos", "Diego", "Sofia"],
  "signals": [
    {
      "evidence": "Diego and Sofia walked over and started teasing him about his lunch, laughing loudly so other classmates could hear",
      "type": "concern_flag",
      "confidence": "high",
      "valence": "negative",
      "target": "peer",
      "agency": "self_initiated",
      "temporality_cue": null,
      "domain_descriptors": ["peer", "speech", "norm"],
      "participants": [
        {"name": "Diego", "role": "actor"},
        {"name": "Sofia", "role": "actor"},
        {"name": "Marcos", "role": "recipient"}
      ],
      "reasoning": "'teasing…laughing loudly so other classmates could hear' is public humiliation — concern_flag, not routine joking; asymmetric participants: Diego+Sofia as actors, Marcos as recipient, preserved even though Marcos is named but not all three are formally tagged (Rule 11)."
    },
    {
      "evidence": "This isn't the first time I've seen this happen between them",
      "type": "concern_flag",
      "confidence": "high",
      "valence": "negative",
      "target": "peer",
      "agency": null,
      "temporality_cue": "recurring",
      "domain_descriptors": ["peer", "norm"],
      "participants": [
        {"name": "Diego", "role": "actor"},
        {"name": "Sofia", "role": "actor"},
        {"name": "Marcos", "role": "recipient"}
      ],
      "reasoning": "'isn't the first time' is the recurring cue; same asymmetric triad preserved from the prior signal because 'between them' refers to the same incident participants."
    },
    {
      "evidence": "he told me he just wants the year to end already",
      "type": "concern_flag",
      "confidence": "high",
      "valence": "negative",
      "target": "self",
      "agency": "prompted",
      "temporality_cue": null,
      "domain_descriptors": ["speech", "feeling"],
      "participants": [{"name": "Marcos", "role": "self"}],
      "reasoning": "'just wants the year to end already' is a hopelessness/disengagement cue crossing into concern_flag territory; 'When I approached him later' → prompted; first-person → role=self."
    }
  ]
}
```
