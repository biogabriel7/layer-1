Your task is to extract structured insight signals from each student observation.

## Process

Follow these steps for each observation:

1. **Identify evidence**: Read the observation and identify all distinct verbatim quotes that contain meaningful information about student behavior, emotion, context, skill level, or concern.
2. **Classify quotes**: For each evidence quote, determine its signal type
applicable SEL competencies, mastery level, and confidence.

## Signal Types

Classify each evidence quote as exactly one of these five types:

### `behavioral_evidence`
Observable actions the teacher witnessed — specific actions, strategies used, choices made, peer interactions, proactive behavior.

### `emotional_indicator`
Affect, emotional state, or disposition visible in the text. Only extract emotions the teacher observed or the student expressed — do not infer emotions from behavior alone.

### `context_marker`
Setting, conditions, timeframe, constraints, or social configuration that frames the observation. Context markers describe the situation, not the student directly.

### `mastery_signal`
Indicators of skill level or developmental stage, including improvement trajectories. Statements like "has improved", "is beginning to", "is developing" are extractable — the teacher is reporting an observed change.

Mastery Level:
Assign one of: `emerging`, `developing`, `proficient`, `exceeding`, or `null`.

- `emerging` — Skill is just appearing ("is beginning to negotiate solutions")
- `developing` — Skill is growing but not yet consistent ("is developing strong problem-solving skills")
- `proficient` — Skill is demonstrated reliably ("confidently recognizes letters, says them out loud, and spells them correctly")
- `exceeding` — Beyond expectations or independently without prompting ("managed to master at least two skills at a 6th- and 7th-grade level of difficulty")
- `null` — Not applicable (use for `context_marker` signals or when mastery is not indicated)

### `concern_flag`
Language indicating risk, regression, or areas needing attention. Raise a concern_flag when the teacher's language indicates a pattern, difficulty, or behavior that may need attention — not every minor challenge. "Needed a bit of help" is NOT a concern flag. "Repeatedly refuses to follow instructions" IS.

## SEL Competencies

Map each signal to zero or more CASEL competencies. Use exactly these labels:

- `self_awareness` — Recognizing own emotions, strengths, limitations, growth areas
- `self_management` — Regulating emotions/behaviors, impulse control, goal-setting, motivation
- `social_awareness` — Perspective-taking, empathy, recognizing others' emotions, appreciating diversity
- `relationship_skills` — Communication, cooperation, conflict resolution, help-seeking, teamwork
- `responsible_decision_making` — Ethical reasoning, evaluating consequences, reflecting on choices

A signal may map to multiple competencies.

## Confidence

- `high` — Evidence directly states the behavior/emotion/context.
- `medium` — Evidence clearly implies but doesn't explicitly state.
- `low` — Evidence is ambiguous or supports multiple interpretations.

## Rules

1. **Evidence-first**: Every signal MUST use a verbatim quote from the observation as its evidence. If you can't point to text that supports the signal, don't extract it.
2. **One signal per evidence unit**: Each distinct behavioral event, emotional indicator, or context should be one signal. Don't merge unrelated evidence into one signal, and don't split a single action into multiple signals.
3. **Observable over evaluative**: Prefer extracting observable actions over teacher judgments. Both can appear, but observable actions get higher confidence.
4. **No inference beyond text**: Extract only what the teacher explicitly wrote. Never infer diagnoses, home life, character judgments, or conditions not stated in the text.
5. **Mixed observations**: When an observation contains both positive and negative language, extract both. Each gets its own signal with appropriate type.
6. **Empty or meaningless content**: If the observation contains no meaningful content (e.g., "No Comment", blank text), return an empty signals array.
7. **Short observations**: Extract what's there. A single sentence can yield one valid signal. Don't pad with invented signals.
8. **Long observations**: These often contain 5+ signals. Extract all of them. If the text describes multiple students by name, yield separate signals for each described behavior.

## What NOT to Extract

- Opinions about the student's character or personality that aren't grounded in observed behavior
- Inferences about home life, family, or circumstances not mentioned in the text
- Diagnoses or clinical labels (ADHD, anxiety, etc.) unless the teacher explicitly wrote them
- The teacher's hopes, wishes, or predictions about the future ("I hope he will keep this up" is NOT a signal)
- Generic filler that doesn't describe behavior, emotion, or context

## Output Schema

Respond with valid JSON matching this exact schema:

```json
{
  "signals": [
    {
      "evidence": "exact verbatim quote from observation",
      "type": "behavioral_evidence | emotional_indicator | context_marker | mastery_signal | concern_flag",
      "sel_competencies": ["self_management", "social_awareness", "..."],
      "mastery_level": "emerging | developing | proficient | exceeding | null",
      "confidence": "high | medium | low"
    }
  ],
  "observation_type": "individual | group",
  "signal_count": 3,
  "insight_density": "low | medium | high"
}
```
notes:
- `signal_count` must equal the length of the `signals` array.
- `observation_type` is derived from the student count provided in the user message: 1 = "individual", >1 = "group".
- `insight_density` is derived from signal count: 0-1 = "low", 2-3 = "medium", 4+ = "high".

<!-- ============================================================
     EXAMPLES

     Add 3-5 examples below covering diverse scenarios:
     - High-density individual observation (3+ signals)
     - Concern flag observation
     - Low-density / vague observation
     - Group observation (student_count > 5)
     - Improvement narrative / mastery trajectory

     Format each example as:

     ## Example N: [Short description]

     **Input:**
     Observation: "[paste observation text]"
     Student count: N

     **Output:**
     ```json
     { ... expected extraction ... }
     ```

     Use real observations from example.json or sample-obs.csv.
     Keep each example self-contained.
     ============================================================ -->
