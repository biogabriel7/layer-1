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

Each signal carries the following facets. Every facet must be derivable from **the exact words of the evidence quote itself** — not surrounding sentences, prior context, or the broader observation. If the quote alone does not contain the cue, set the facet to `null` (or leave it out of the list).

**Default rule: prefer `null` over a best guess.** Over-extraction is a worse failure than under-extraction. If you cannot point to specific words in the evidence quote that cue a facet value, leave it `null`. Pronouns in the quote (`you`, `us`, `them`, `someone`) are not cues for `target` or `participants`. Implicit social context ("social interactions", "in class", "with friends in playground") is not a cue for `target` unless the explicit cue word from the target list appears.

Concretely:

- No adult named in the quote → do not add `adult` to `domain_descriptors`.
- No explicit change cue in the quote ("improved", "now", "started to") → `temporality_cue` stays `null`, even if the surrounding observation implies progression.
- Name appears only earlier in the observation but not in the quote → do not add that name to `participants`.
- Broader word like "others" in the quote → use `group`, not `peer`.

When the text does not support a value, use `null` (or `[]` for list fields) — never guess.

### `confidence`
Categorical — how clearly the evidence supports the signal.

- `high` — Evidence directly states the behavior/emotion/context, describing specific actions, words, strategies, or moments grounded in what was directly seen or heard with minimal judgment.
- `medium` — Evidence clearly implies but doesn't explicitly state — some detail about what happened, but still broad, missing key context, or mixing observation with opinion.
- `low` — Evidence is ambiguous or supports multiple interpretations — vague or generic statements, or opinions, labels, and judgments with no observable evidence.

Canonical low-confidence phrasings: "Did well today" / "Good work in math" / "Needs improvement" / "Is very smart" / "Isn't trying hard enough" / "Has a great attitude".

### `valence`
Sentiment of the signal — reflects the teacher's framing of whether the evidence is positive, negative, both, or neither.

- `positive` — Framed approvingly or as growth/success ("thrived", "helped", "mastered", "improved").
- `negative` — Framed as struggle, concern, or deficit ("struggled", "refused", "couldn't", "disengaged").
- `mixed` — Contains both positive and negative framing ("he enjoyed it, but at the beginning he was bored").
- `neutral` — Factual framing with no clear valence ("During recess", "worked on fractions", "split into teams").
- `null` — Genuinely ambiguous; do not force.

### `target`
Coarse category describing what or whom the signal is about.

Populate `target` **only** when the quote contains an explicit cue for one of the categories below. Do not infer target from surrounding context or the implied audience.

- `self` — Cues: self-reference ("himself", "herself", "themselves", "his own", "her own"), or the student's own state ("he was tired", "she told me she was proud").
- `peer` — Cues: a **singular** other-student reference ("a classmate", "a peer", "her partner", "a friend", "one of his classmates"). Singular only — "a friend" is peer, "friends" (plural) is group.
- `group` — Cues: **plural or collective** references ("peers", "classmates", "others", "friends" (plural), "the team", "his crew", "the group").
- `adult` — Cues: "the teacher", "the adult", "me" (when the teacher narrates a direct interaction).
- `task` — Cues: a specific academic activity or problem ("the problem", "the worksheet", "the assignment", "the project", "writing", "reading", "the math task").
- `object` — Cues: a physical object or material ("a block", "the number line", "the dictionary").
- `environment` — Cues: the setting or event itself ("during recess", "at circle time", "in the playground", "during Empathy Week").
- `null` — No cue from the lists above appears in the quote. This is the default for generic behavioral descriptions ("responding with politeness", "active listening", "behaves well").

### `agency`
How the behavior came about — populate **only** when the text explicitly states it.

Populate `agency` **only** when the quote contains one of the explicit cue phrases below. Never infer agency from the behavior itself.

- `self_initiated` — Cues: "without being asked", "by herself" / "by himself" / "by themselves", "on her/his/their own", "on her/his/their own initiative", "independently", "initiates" / "initiated" (when used of the student starting an action), "decided to", "proactively". The verb `chose`/`choose` alone is **not** sufficient — choosing between provided options in a structured activity isn't self-initiation.
- `prompted` — Cues: "when I reminded", "after being asked", "with [some] prompt(ing)", "when I asked".
- `scaffolded` — Cues: "after one-on-one support", "with guidance from", "with the teacher's help", "with support from".
- `external` — Cues: something explicitly outside the student's choice interrupts or redirects ("the fire alarm interrupted", "the teacher redirected him").
- `null` — No cue phrase from the lists above appears in the quote. This is the default.

### `temporality_cue`
Whether the evidence is explicitly marked as a change, pattern, or first occurrence — populate **only** when the text uses a cue.

Populate `temporality_cue` **only** when the quote contains one of the explicit cue words below. Verb aspect alone is not a cue.

- `first_time` — Cues: "for the first time", "had never before", "today was the first".
- `recurring` — Cues: "often", "usually", "consistently", "repeatedly", "tends to", "still [verbs]", "continues to", "this [X] wasn't new".
- `change` — Cues: "has improved", "started to", "is now [doing]", "used to [X] but now [Y]".
- `one_time` — Cues: "today", "during this session", "this morning", "at recess today".
- `null` — No cue word from the lists above appears in the quote. This is the default.

**Not temporality cues:**
- Habitual present-tense aspect alone ("enjoys", "writes", "uses", "chooses", "creates") → `null`.
- Continuous aspect alone ("making", "offering", "writing") → `null`.
- Capability markers ("is learning to", "is developing", "is beginning to", "was able to") → these signal capability (see Rule 10), not change. `temporality_cue: null`.

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

A single signal can carry multiple descriptors when the evidence touches several. An empty list `[]` is valid when none apply (e.g., a pure context_marker about a date).

**Important:** `object` is a valid value for the `target` facet, **not** for `domain_descriptors`. Never put `object` in this list — it will fail validation.

### `participants`
Array of objects identifying named humans referenced in the evidence and their role in the action.

```json
"participants": [
  {"name": "Juan",   "role": "actor"},
  {"name": "Marcos", "role": "recipient"}
]
```

- `name` — **Layer 1 is quote-literal. Emit a participant entry only when the quote contains one of these explicit human references. Match the whole phrase, not a pronoun or verb:**

  - **Proper name** literally in the quote ("Clara", "Romeo") → `{"name": "<exact name>", "role": ...}`.
  - **Exact noun phrase** literally in the quote — one of: `"the student"`, `"a student"`, `"one student"`, `"some students"`, `"a classmate"`, `"a peer"`, `"her peers"` / `"his peers"` / `"their peers"`, `"his crew"` / `"her crew"` / `"their crew"` → `{"name": null, "role": ...}`.

  Anything else → do **not** emit an entry. In particular:
  - Pronouns only (`she`, `he`, `they`, `her`, `his`, `their`, `them`) → `participants: []`.
  - Implicit subject (quote starts with a verb like `"making deep connections..."`, `"encouraging kindness..."`, `"is learning to..."`) → `participants: []`.
  - Even if a proper name appears elsewhere in the observation (e.g., in `named_students`), do not resolve a pronoun or implicit subject to that name. Downstream layers handle resolution.
- `role` — One of:
  - `actor` — Performs the behavior the evidence describes.
  - `recipient` — Receives the behavior described (the target of an action by others).
  - `self` — The named person is **speaking about themselves in first person** (e.g., "he told me he felt proud", "she said she couldn't do it"). Teacher-reported dispositions or feelings ("Clara enjoys writing", "he seemed happy") are NOT `self` — use `actor` instead, because the teacher is reporting the student's state.
  - `group_member` — One of several doing the same thing; used when the evidence describes a group and the named person is part of that group.
  - `bystander` — Mentioned as present but not directly involved in the behavior.
  - `null` — When role cannot be determined.

Multiple entries per signal when several people share a role (e.g., two actors, one recipient). Use `[]` when no humans are relevant to the signal (e.g., a context_marker about the setting).

**Important:** populate `participants` based on what the evidence quote says, regardless of whether a named student is formally tagged on the observation. If the observation names a third student who isn't in the tagged set but participates in the evidence, still record them — this surfaces important asymmetries downstream.

## Observation-level fields

These apply to the observation as a whole (not a single signal).

- **`language`** — The predominant language of the observation text. Use ISO-like two-letter codes: `en`, `es`, `pt`, etc. If the observation mixes languages, use the predominant one.
- **`source_type`** — Always `"teacher_observation"` for this iteration. (Reserved for future source types like self-reflection, family observation, guided activity — do not use those values.)
- **`named_students`** — Array of all proper-name references found anywhere in the observation text. Preserve original spelling. Include every name, even if the student is not formally tagged on the observation. Empty list `[]` when no names appear.

The following fields are computed deterministically and will be enforced downstream regardless of what you return — you may omit them or return any value; the post-processor overwrites them:

- `student_count` — pass-through from input.
- `observation_type` — `"individual"` if `student_count == 1`, else `"group"`.
- `signal_count` — `len(signals)`.
- `insight_density` — 0–1 signals → `"low"`, 2–3 → `"medium"`, 4+ → `"high"`.
- `named_students_count` — `len(named_students)`.
- `meaningful_content` — `true` when `signal_count > 0`, else `false`.

## Rules

1. **Evidence-first.** Every signal MUST anchor to a verbatim quote from the observation. If you cannot point to text that supports the signal, do not extract it.
2. **One signal per evidence unit.** A unit is defined by meaning, not by sentence boundaries:
   - A single coherent action across multiple clauses is one unit ("She walked over to the new student and introduced herself").
   - A sentence describing multiple distinct skills, subjects, or moments is multiple units — split it ("He wrote a paragraph and spelled every word correctly" → two signals).
   - A pattern plus its supporting incident is one unit when merging preserves the escalation or causal structure that gives the signal its meaning. This applies especially to `concern_flag`, where a full multi-sentence observation can be a single signal.
   - Tie-breaker: if splitting removes context needed to classify type or confidence, keep merged. If merging hides a distinct second signal, split.
3. **Observable over evaluative.** When the teacher pairs a judgment ("showed leadership", "demonstrated curiosity") with a concrete action describing the same moment, extract only the action. Judgments are interpretation; actions are evidence. For **standalone evaluative language with no concrete action**:
   - **Dispositional** ("enjoys reading", "loves writing", "is passionate about X") → classify as `emotional_indicator` (teacher-reported affect), not `behavioral_evidence`. "Enjoys" names a feeling, not a witnessed action.
   - **Character label** ("is a balanced girl", "is responsible", "has a great attitude", "is a good kid") → do not extract, even when surrounded by contextual framing. "Is a balanced girl during quiet time" still has `"is a balanced girl"` as its evidence core — the label is the signal, and a label is not evidence. Drop the whole candidate. (Exception: `concern_flag` when the label itself names a pattern requiring attention, e.g., "is consistently disruptive".)
   - **Teacher recommendation or reflection** ("should continue to work on this", "needs to improve", "this shows the value of X") → do not extract. These belong to the "What NOT to extract" list.

   Exception: if an evaluative phrase reports the student's own expressed feeling ("he said he felt proud"), keep it as `emotional_indicator`.
4. **No inference beyond text.** Extract only what the teacher explicitly wrote. Never infer diagnoses, home life, character judgments, or conditions not stated. Never infer framework competencies, mastery levels, or curricular alignment — those belong to later layers of the pipeline.
5. **Never force a facet.** `agency`, `temporality_cue`, `valence`, `target`, and `participants[].name` all accept `null`. When the evidence does not support a value, use `null`. A well-extracted signal may have several `null` facets; that is a feature, not a failure.
6. **Mixed observations.** When an observation contains both positive and negative language, extract both, each as its own signal with appropriate valence.
7. **Empty or meaningless content.** If the observation contains no meaningful content ("No Comment", blank, "N/A"), return an empty signals array. The post-processor will set `meaningful_content: false` automatically.
8. **Match output to input.** A short observation may yield one signal; don't pad. A long observation often contains 5+ signals; extract them all. When multiple students are named, yield separate signals for each when the evidence supports distinct behaviors.
9. **Group observations with unnamed actors.** When a group observation references an unnamed actor ("one student", "a member", "some", "a few"), confidence is capped at `medium` because the action cannot be attributed, and the corresponding `participants` entry has `name: null`. When two or more unnamed subgroups are described with conflicting states ("some said X, others said Y"), do not extract — there is no attributable subject.
10. **Capability vs. observed action.** When the evidence quote contains an explicit capability marker (`can`, `could`, `is able to`, `was able to`, `is beginning to`, `is learning to`, `is developing`), `confidence` is **strictly capped at `low`**. Do not lift this cap based on generic verbs in the rest of the sentence — "was able to create their story" is still capability language, not a witnessed instance. The cap lifts only when the same quote contains a concrete, specific, measurable action with observable detail (e.g., "she solved 4 ÷ 2 by drawing dots", "he wrote 'the cat sat on the mat' independently"). When in doubt, keep the cap. Present-tense habitual verbs without capability markers (`uses`, `writes`, `spells`, `joins`, `creates`, `makes`) are observed actions, not capability — not subject to the cap.
11. **Multi-participant asymmetry.** A single observation can produce signals with different valence and role attribution for different participants. When the text describes an action involving multiple named students (one acting on another), extract signals per-participant-role even when only some of them are formally tagged — the `participants` field carries the asymmetry.
12. **Reasoning required.** Each signal must include a `reasoning` string that justifies the type, confidence, and any non-trivial facet choices by referencing the specific words in the evidence. Address concern-flag threshold decisions explicitly ("why this crosses from minor challenge into flaggable concern"). Justify the choices you made; you do not need to explain alternatives you did not choose.

## What NOT to extract

- Teacher judgments about character, personality, or potential not grounded in a witnessed action (extract the action instead — see Rule 3).
- Inferences about home life, family, or circumstances not mentioned in the text.
- Diagnoses or clinical labels (ADHD, anxiety, etc.) unless the teacher explicitly wrote them.
- Framework competencies (CASEL, IB ATL, etc.), mastery levels, or curricular alignments — these belong in later pipeline stages.
- Hopes, wishes, or predictions about the future ("I hope he will keep this up").
- Teacher reflections on lesson value or takeaways ("we discussed how listening is important", "this shows the value of teamwork") — these describe the teacher's framing, not student behavior.
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

### Example 1: High-density individual observation with a concern flag and a change-over-time arc.

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
      "reasoning": "Type: context_marker because 'During the Tribe Meet' names the activity framing the observation — it describes a situation, not a student action or emotion. Confidence: high because the event is named unambiguously. Valence: neutral — no evaluative framing. Target: environment because it refers to the ritual setting. Domain: norm because Tribe Meet is a community ritual. No participants because the context piece names no one."
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
      "reasoning": "Type: concern_flag because 'This attitude wasn't new' signals a recurring pattern of disengagement, elevating it beyond a one-off action. Valence: negative — refusal of group participation. Target: group because the game is a group activity. Agency: self_initiated because 'chose' explicitly states deliberate choice. Temporality: recurring — 'wasn't new' explicitly marks the pattern. Concern threshold: 'wasn't new' is the key phrase marking this as pattern-level rather than a single refusal."
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
      "reasoning": "Type: behavioral_evidence because 'decided to join' is a specific observable action. Valence: positive — participation shift. Agency: self_initiated from 'decided'. Temporality: change because this contradicts the earlier refusal — the text explicitly marks the shift. Confidence: high because the moment and timing ('after about ten minutes') are concrete."
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
      "reasoning": "Type: behavioral_evidence because the teacher describes observing participation and engagement; 'seemed to enjoy' is teacher inference so this is not an emotional_indicator (the student did not express the feeling). Confidence: medium because 'seemed' indicates interpretation rather than direct report. Valence: positive. Target: group. Temporality: one_time — the observation is a single moment."
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
      "reasoning": "Type: emotional_indicator because the student directly reports his own feelings ('enjoyed', 'bored'). Valence: mixed because both positive (enjoyed) and negative (bored) are reported. Target: self — Romeo speaking about his own emotional experience. Temporality: change — explicit shift from bored to enjoyed. Role: self because he is speaking about his own state. Confidence: high — direct first-person report."
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
      "reasoning": "Type: concern_flag because the language goes beyond transient feeling — 'can't find his own place' frames a persistent belonging difficulty. Valence: negative. Target: self because Romeo reflects on his own relationship to the group. Temporality: recurring — 'can't find' frames an ongoing inability. Domain: speech (he verbalizes), feeling (emotional content), peer (group relation). Concern threshold: 'can't find his own place' and 'doesn't like the group' signal a persistent belonging struggle, not a single social adjustment."
    }
  ]
}
```

### Example 2: Vague group observation with a low-confidence signal and no named students.

**Input**
Observation: "Good collaboration with all his colleagues on the collaborative paint project"

Student Count: 4

**Output**
```json
{
  "language": "en",
  "source_type": "teacher_observation",
  "named_students": [],
  "signals": [
    {
      "evidence": "Good collaboration with all his colleagues on the collaborative paint project",
      "type": "behavioral_evidence",
      "confidence": "low",
      "valence": "positive",
      "target": "peer",
      "agency": null,
      "temporality_cue": "one_time",
      "domain_descriptors": ["peer", "creation", "task"],
      "participants": [],
      "reasoning": "Type: behavioral_evidence because 'collaboration' refers to an observable action (working together). Confidence: low because 'good collaboration' is evaluative with no specific actions, interactions, or behaviors described — the evidence could describe anything from active leadership to passive compliance. Valence: positive — framed approvingly. Target: peer because the action is with 'his colleagues'. Agency: null — the text does not state how the collaboration started. Temporality: one_time — tied to a specific project. Domain: peer (with classmates), creation (paint project produces an artifact), task (structured activity). Participants: empty list because no one is named despite four students being tagged."
    }
  ]
}
```

### Example 3: Individual observation with a concern flag and a scaffolded academic arc.

**Input**
Observation: "Jasmine had difficulty grasping the decomposing method at first, as she wasn't fully engaged during the group activity. However, after one-on-one support, she understood the concept. She was able to decompose numbers from 2 to 6 by herself but eventually became frustrated and started crying, saying she \"can't do hard things.\" She tends to get discouraged easily when working alone and needs encouragement to build resilience and confidence in tackling challenges"

Student Count: 1

**Output**
```json
{
  "language": "en",
  "source_type": "teacher_observation",
  "named_students": ["Jasmine"],
  "signals": [
    {
      "evidence": "Jasmine had difficulty grasping the decomposing method at first",
      "type": "behavioral_evidence",
      "confidence": "medium",
      "valence": "negative",
      "target": "task",
      "agency": null,
      "temporality_cue": "one_time",
      "domain_descriptors": ["task"],
      "participants": [{"name": "Jasmine", "role": "actor"}],
      "reasoning": "Type: behavioral_evidence because 'had difficulty grasping' describes an observable performance outcome. Confidence: medium because the specific behaviors underlying the judgment (confusion, wrong answers) are not described. Valence: negative — framed as struggle. Target: task — the academic method. Temporality: one_time — 'at first' frames a moment, no pattern language. Not concern_flag because a single instance of difficulty with a new concept is a normal learning challenge."
    },
    {
      "evidence": "she wasn't fully engaged during the group activity",
      "type": "behavioral_evidence",
      "confidence": "medium",
      "valence": "negative",
      "target": "group",
      "agency": null,
      "temporality_cue": "one_time",
      "domain_descriptors": ["task", "peer"],
      "participants": [{"name": "Jasmine", "role": "actor"}],
      "reasoning": "Type: behavioral_evidence because it describes her participation level. Confidence: medium because 'wasn't fully engaged' is a subjective judgment without specific disengaged behaviors described. Valence: negative. Target: group — the group activity. Agency: null because the text does not explain how or why she disengaged."
    },
    {
      "evidence": "after one-on-one support, she understood the concept",
      "type": "behavioral_evidence",
      "confidence": "medium",
      "valence": "positive",
      "target": "task",
      "agency": "scaffolded",
      "temporality_cue": "change",
      "domain_descriptors": ["task", "adult"],
      "participants": [{"name": "Jasmine", "role": "actor"}],
      "reasoning": "Type: behavioral_evidence — an outcome (understanding) is described. Agency: scaffolded because 'after one-on-one support' explicitly names adult support as the condition for the shift. Temporality: change — explicit shift from not understanding to understanding. Target: task — the concept. Domain: task and adult (scaffolded by an adult). Confidence: medium because the specific evidence of understanding is not described."
    },
    {
      "evidence": "She was able to decompose numbers from 2 to 6 by herself",
      "type": "behavioral_evidence",
      "confidence": "high",
      "valence": "positive",
      "target": "task",
      "agency": "self_initiated",
      "temporality_cue": "one_time",
      "domain_descriptors": ["task"],
      "participants": [{"name": "Jasmine", "role": "actor"}],
      "reasoning": "Type: behavioral_evidence — a specific, measurable academic action. Confidence: high because 'from 2 to 6' and 'by herself' are concrete and unambiguous. Agency: self_initiated from 'by herself'. Valence: positive — a demonstrated success. Target: task."
    },
    {
      "evidence": "eventually became frustrated and started crying, saying she \"can't do hard things.\"",
      "type": "concern_flag",
      "confidence": "high",
      "valence": "negative",
      "target": "self",
      "agency": null,
      "temporality_cue": null,
      "domain_descriptors": ["body", "speech", "feeling"],
      "participants": [{"name": "Jasmine", "role": "actor"}],
      "reasoning": "Type: concern_flag because frustration, crying, and a global self-defeating statement ('can't do hard things') combine into an emotional escalation warranting attention. Valence: negative. Target: self — the self-statement is about herself. Domain: body (crying), speech (saying), feeling (frustration). Temporality: null for the evidence boundary alone; the surrounding sentence 'tends to get discouraged easily' marks a pattern but was not included in this quote. Concern threshold: 'started crying' and the absolute 'can't do hard things' indicate emotional overwhelm beyond routine frustration."
    }
  ]
}
```

### Example 4: Multi-participant asymmetry — observation tagged to two students but names a third.

**Input**
Observation: "During recess today, Marcos was sitting alone by the fence, and I noticed that Diego and Sofia walked over and started teasing him about his lunch, laughing loudly so other classmates could hear. This isn't the first time I've seen this happen between them. Marcos got up and walked away without saying anything. When I approached him later, he told me he just wants the year to end already."

Student Count: 2

**Output**
```json
{
  "language": "en",
  "source_type": "teacher_observation",
  "named_students": ["Marcos", "Diego", "Sofia"],
  "signals": [
    {
      "evidence": "During recess today",
      "type": "context_marker",
      "confidence": "high",
      "valence": "neutral",
      "target": "environment",
      "agency": null,
      "temporality_cue": "one_time",
      "domain_descriptors": ["norm"],
      "participants": [],
      "reasoning": "Type: context_marker — names the setting. Target: environment. Temporality: one_time — 'today' frames a single occurrence. No participants because the context piece names no one."
    },
    {
      "evidence": "Marcos was sitting alone by the fence",
      "type": "behavioral_evidence",
      "confidence": "high",
      "valence": "negative",
      "target": "self",
      "agency": null,
      "temporality_cue": null,
      "domain_descriptors": ["body", "peer"],
      "participants": [{"name": "Marcos", "role": "actor"}],
      "reasoning": "Type: behavioral_evidence — a specific observable state (sitting alone). Valence: negative — social isolation is framed implicitly as a concerning position (context makes this a precursor to what follows). Target: self — solo state. Domain: body (physical position) and peer (social isolation relative to peers). Agency: null — the text does not state whether he chose solitude or was excluded."
    },
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
      "reasoning": "Type: concern_flag — teasing amplified for audience exposure is behavior needing attention, not routine peer interaction. Valence: negative. Target: peer — directed at Marcos. Agency: self_initiated — Diego and Sofia chose to approach and tease. Domain: peer (between students), speech (verbal teasing), norm (violation of community expectation). Participants: asymmetric — Diego and Sofia are actors, Marcos is recipient. Marcos is named but not in the tagged student_count=2 set; the asymmetry is preserved here. Concern threshold: 'teasing', 'laughing loudly so other classmates could hear' indicates public humiliation, not casual joking."
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
      "reasoning": "Type: concern_flag — teacher explicitly marks this as a pattern. Temporality: recurring — 'isn't the first time' is the pattern cue. Valence: negative. Target: peer. Participants: same asymmetric triad as the prior signal, per Rule 11 (multi-participant asymmetry is preserved). No agency because the sentence is teacher framing, not a student action."
    },
    {
      "evidence": "Marcos got up and walked away without saying anything",
      "type": "behavioral_evidence",
      "confidence": "high",
      "valence": "mixed",
      "target": "self",
      "agency": "self_initiated",
      "temporality_cue": null,
      "domain_descriptors": ["body", "peer"],
      "participants": [{"name": "Marcos", "role": "actor"}],
      "reasoning": "Type: behavioral_evidence — observable action (got up, walked away). Valence: mixed — withdrawing is self-protective (positive framing possible) but also avoids addressing the situation (negative framing possible). Agency: self_initiated — he chose to leave. Target: self — his own exit. Domain: body (movement) and peer (reaction to the peer interaction)."
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
      "reasoning": "Type: concern_flag — a global dismissive statement about wanting the school year to end signals emotional distress that warrants attention, beyond routine frustration. Valence: negative. Target: self — he is expressing about his own state. Agency: prompted — 'When I approached him later' cues that the adult initiated the conversation. Role: self — he speaks about himself. Concern threshold: 'just wants the year to end already' is a disengagement/hopelessness cue that crosses from frustration into flaggable territory."
    }
  ]
}
```
