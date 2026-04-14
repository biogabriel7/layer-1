Your task is to extract structured insight signals from each student observation.

## Process

Follow these steps for each observation:

1. **Identify evidence**: Read the observation and identify all distinct verbatim quotes that contain meaningful information about student behavior, emotion, context, skill level, or concern.
2. **Classify quotes**: For each evidence quote, determine its signal type, applicable SEL competencies, and confidence.

## Signal Types

Classify each evidence quote as exactly one of these four types:

### `behavioral_evidence`
Observable actions the teacher witnessed — specific actions, strategies used, choices made, peer interactions, proactive behavior.

### `emotional_indicator`
Affect, emotional state, or disposition visible in the text. Only extract emotions the teacher observed or the student expressed — do not infer emotions from behavior alone.

### `context_marker`
Setting, conditions, timeframe, constraints, or social configuration that frames the observation. Context markers describe the situation, not the student directly.

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
      "type": "behavioral_evidence | emotional_indicator | context_marker | concern_flag",
      "sel_competencies": ["self_management", "social_awareness", "..."],
      "confidence": "high | medium | low"
    }
  ]
}
```

## Examples

### Example 1: High density comment with a concern flag along with irrelevant teacher comments at the end (last 3 sentences).

**Input**
Observation: ""During the Tribe Meet, Romeo chose not to join the game we played. This attitude wasn’t new, but after about ten minutes he decided to join, and his colleagues welcomed him. I saw Romeo having fun in the game, and he seemed to enjoy being part of the team. Later, when we walked back to school, I asked him how the experience felt. He told me that he enjoyed it, but at the beginning he was bored and didn’t want to take part. His main concern was that he can’t find his own place in the tribe, which makes him feel like he doesn’t like the group. I encouraged him to get more involved in the games we play and to be a bit more open with his crew members. Many activities are designed to help the group connect and collaborate. By participating, he can make new friends and slowly find his own place in the tribe."

Student count: 1

**Output**
```json
{
  "signals": [
    {
      "evidence": "During the Tribe Meet",
      "type": "context_marker",
      "sel_competencies": [],
      "confidence": "high"
    },
    {
      "evidence": "Romeo chose not to join the game we played. This attitude wasn’t new",
      "type": "concern_flag",
      "sel_competencies": [],
      "confidence": "high"
    },
    {
      "evidence": "after about ten minutes he decided to join",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "confidence": "high"
    },
    {
      "evidence": "I saw Romeo having fun in the game, and he seemed to enjoy being part of the team.",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "confidence": "medium"
    },
    {
      "evidence": "He told me that he enjoyed it, but at the beginning he was bored and didn’t want to take part",
      "type": "emotional_indicator",
      "sel_competencies": ["self_awareness"],
      "confidence": "high"
    },
    {
      "evidence": "His main concern was that he can’t find his own place in the tribe, which makes him feel like he doesn’t like the group",
      "type": "concern_flag",
      "sel_competencies": ["self_awareness", "social_awareness"],
      "confidence": "high"
    }
  ]
}
```

### Example 2: Vague comment with low confidence. No clear actions given on how they were collaborating well.

**Input**
Observation:"Good collaboration with all his colleagues on the collaborative paint project"
Student Count: 4

**Output**
```json
{
  "signals": [
    {
      "evidence": "Good collaboration with all his colleagues on the collaborative paint project",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "confidence": "low"
    }
  ]
}
```

### Example 3: Concern flag with medium and low confidence signals that do not match any SEL competencies.
**Input**
Observation: "Jasmine had difficulty grasping the decomposing method at first, as she wasn’t fully engaged during the group activity. However, after one-on-one support, she understood the concept. She was able to decompose numbers from 2 to 6 by herself but eventually became frustrated and started crying, saying she ""can't do hard things."" She tends to get discouraged easily when working alone and needs encouragement to build resilience and confidence in tackling challenges"

Student Count: 1

**Output**
```json
{
  "signals": [
    {
      "evidence": "Jasmine had difficulty grasping the decomposing method at first",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "confidence": "medium"
    },
    {
      "evidence": "she wasn’t fully engaged during the group activity",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "confidence": "medium"
    },
    {
      "evidence": "after one-on-one support, she understood the concept",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "confidence": "medium"
    },
    {
      "evidence": "She was able to decompose numbers from 2 to 6 by herself",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "confidence": "high"
    },
    {
      "evidence": "eventually became frustrated and started crying, saying she \"can’t do hard things.\"",
      "type": "concern_flag",
      "sel_competencies": [],
      "confidence": "high"
    }
  ]
}
```
