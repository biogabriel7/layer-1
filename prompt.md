Your task is to extract structured insight signals from each student observation.

## Process

Follow these steps for each observation:

1. **Identify evidence**: Read the observation and identify all distinct verbatim quotes that contain meaningful information about student behavior, emotion, context, skill level, or concern.
2. **Classify quotes**: For each evidence quote, determine its signal type, applicable SEL competencies, and observation confidence.
3. **Reason through each signal**: For each signal, write a reasoning string that addresses these classification decisions: (a) why this signal type was chosen and what alternatives were ruled out, (b) why these specific SEL competencies apply or why none do, (c) what about the evidence drives the confidence level, (d) why the evidence quote starts and ends where it does — what makes this a single evidence unit rather than something that should be split or merged with adjacent text (address this when the observation contains compound sentences or sequential actions where the boundary is non-obvious), and (e) (concern_flag signals only) why the language crosses from minor challenge into flaggable concern — reference the specific words that indicate a pattern, difficulty, or behavior needing attention rather than a routine struggle (e.g., "repeatedly", "can't control", "refuses" vs. "needed a bit of help"). Be specific — reference the actual words in the evidence that informed each decision.

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

## Observation Confidence

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
      "observation_confidence": "high | medium | low",
      "reasoning": "Explain: (a) why this type was chosen over alternatives, (b) why these SEL competencies apply or why none do, (c) what in the evidence drives the confidence level, (d) why the evidence boundary was drawn here (when non-obvious), (e) [concern_flag only] why this crosses from minor challenge into flaggable concern"
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
      "observation_confidence": "high",
      "reasoning": "Type: context_marker because 'During the Tribe Meet' identifies the setting and activity framing the observation — it describes a situation, not a student action or emotion, ruling out behavioral_evidence and emotional_indicator. It is not a concern because it carries no evaluative language. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: high because the teacher explicitly and unambiguously names the specific event."
    },
    {
      "evidence": "Romeo chose not to join the game we played. This attitude wasn’t new",
      "type": "concern_flag",
      "sel_competencies": [],
      "observation_confidence": "high",
      "reasoning": "Type: concern_flag rather than behavioral_evidence because the phrase ‘This attitude wasn’t new’ signals a recurring pattern of disengagement the teacher finds noteworthy — this elevates it beyond a one-off action into something needing attention. Competencies: none, because the refusal to participate does not demonstrate any SEL competency; it could relate to self_management, but the text shows a deficit rather than a demonstrated skill, and we map competencies to what is shown, not what is lacking. Confidence: high because the teacher directly states both the specific behavior (‘chose not to join’) and its recurrence (‘wasn’t new’), leaving no ambiguity. Signal boundary: the two sentences are merged because the first (‘chose not to join the game’) describes the behavior and the second (‘This attitude wasn’t new’) qualifies it as a pattern — together they form a single evidence unit; splitting them would lose the recurrence context that makes this a concern rather than a one-off action. Concern threshold: ‘This attitude wasn’t new’ is the key phrase — it explicitly marks the behavior as recurring, crossing from a single refusal (routine) into a pattern needing attention."
    },
    {
      "evidence": "after about ten minutes he decided to join",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high",
      "reasoning": "Type: behavioral_evidence because 'he decided to join' is a specific, observable action the teacher witnessed — not an emotion or a setting detail. It is not a concern_flag because joining is a positive behavioral shift, not a risk indicator. Competencies: self_management because the student regulated his initial reluctance and made a deliberate choice to participate without being forced — this reflects impulse control and self-motivation. Not relationship_skills because the decision to join was internal, not prompted by peer interaction. Confidence: high because the teacher directly observed the moment he joined and specifies the approximate timing ('after about ten minutes'), making this concrete and unambiguous."
    },
    {
      "evidence": "I saw Romeo having fun in the game, and he seemed to enjoy being part of the team.",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "observation_confidence": "medium",
      "reasoning": "Type: behavioral_evidence because the teacher describes observing Romeo participating (‘having fun in the game’) and engaging with others (‘being part of the team’) — these are witnessed actions. Not emotional_indicator because the enjoyment is inferred by the teacher (‘seemed to enjoy’) rather than expressed by the student himself. Competencies: relationship_skills because being part of a team game and engaging positively with peers demonstrates cooperation and teamwork. Not social_awareness because the evidence shows participation, not perspective-taking or empathy toward others. Confidence: medium because the word ‘seemed’ indicates the teacher is interpreting Romeo’s internal state rather than reporting a directly stated or clearly observable behavior — the fun is inferred from body language or demeanor, not explicitly confirmed. Signal boundary: the two clauses are joined because both describe the same observed moment — having fun and enjoying being part of the team are a single behavioral snapshot, not two distinct events; splitting at the comma would create an incomplete observation on each side."
    },
    {
      "evidence": "He told me that he enjoyed it, but at the beginning he was bored and didn’t want to take part",
      "type": "emotional_indicator",
      "sel_competencies": ["self_awareness"],
      "observation_confidence": "high",
      "reasoning": "Type: emotional_indicator because the student directly communicated his feelings — ‘he enjoyed it’, ‘he was bored’, ‘didn’t want to take part’ — these are self-reported emotional states, not teacher-observed actions. Not behavioral_evidence because the core content is about how the student felt, not what he did. Competencies: self_awareness because Romeo is recognizing and articulating his own emotional states (enjoyment, boredom, reluctance) in a reflective conversation — this is a clear demonstration of identifying and naming one’s own feelings. Not self_management because the evidence describes awareness of emotions, not regulation of them. Confidence: high because these are the student’s own reported words conveyed through direct dialogue (‘He told me that...’), giving the teacher first-hand access to the student’s emotional experience with no inference required."
    },
    {
      "evidence": "His main concern was that he can’t find his own place in the tribe, which makes him feel like he doesn’t like the group",
      "type": "concern_flag",
      "sel_competencies": ["self_awareness", "social_awareness"],
      "observation_confidence": "high",
      "reasoning": "Type: concern_flag because the student's expressed inability to find his place and resulting negative feelings toward the group ('feel like he doesn't like the group') indicate an ongoing social-emotional struggle that warrants teacher attention. Not emotional_indicator alone because the language goes beyond reporting a transient feeling — it describes a persistent relational difficulty. Competencies: self_awareness because the student recognizes and names his own feelings of not belonging ('can't find his own place'); social_awareness because he is reflecting on his relationship to the group dynamic and how it affects his feelings toward others. Not relationship_skills because the evidence describes a struggle with group connection, not a demonstrated communication or cooperation skill. Confidence: high because the student directly stated this concern in his own words ('His main concern was that...'), providing unambiguous first-person evidence of both the struggle and its emotional impact. Concern threshold: 'can't find his own place' and 'feel like he doesn't like the group' indicate a persistent belonging struggle — the student frames it as an ongoing inability ('can't find'), not a one-time difficulty, and the emotional consequence (disliking the group) signals escalation beyond a routine social adjustment."
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
      "observation_confidence": "low",
      "reasoning": "Type: behavioral_evidence because 'collaboration' refers to an observable action (working together on a project), not an emotion or setting. Not context_marker because the collaborative paint project is the activity the student participated in, not just a framing detail — the teacher is evaluating the student's participation. Not emotional_indicator because no feelings are described. Competencies: relationship_skills because collaboration on a group project directly demonstrates cooperation and teamwork with peers. Not social_awareness because there is no evidence of perspective-taking or empathy — only joint work. Confidence: low because the teacher uses the evaluative term 'good collaboration' without describing any specific actions, interactions, or behaviors that demonstrate what the collaboration looked like — the evidence is ambiguous and could describe anything from active leadership to passive compliance."
    }
  ]
}
```

### Example 3: Concern flag with medium and low observation confidence signals that do not match any SEL competencies.
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
      "observation_confidence": "medium",
      "reasoning": "Type: behavioral_evidence because ‘had difficulty grasping the decomposing method’ describes an observable academic performance outcome the teacher witnessed. Not concern_flag because a single instance of difficulty with a new concept is a normal learning challenge, not a pattern or risk indicator — the threshold for concern_flag requires recurring or escalating issues. Competencies: none, because struggling with an academic concept is a learning event, not a demonstration of any SEL competency. Not self_management because there is no evidence of the student attempting to regulate or self-correct here. Confidence: medium because ‘had difficulty grasping’ is the teacher’s interpretive assessment of the student’s understanding — the teacher observed something that led to this conclusion, but the specific behaviors underlying the judgment (confusion, wrong answers, etc.) are not described."
    },
    {
      "evidence": "she wasn’t fully engaged during the group activity",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "medium",
      "reasoning": "Type: behavioral_evidence because ‘wasn’t fully engaged during the group activity’ describes the teacher’s observation of the student’s participation level — an observable behavior. Not concern_flag because a single instance of partial disengagement in one activity does not meet the threshold of a recurring pattern or risk. Not context_marker because this describes the student’s behavior, not the setting. Competencies: none, because lack of engagement does not demonstrate any SEL competency. One might consider self_management (lack of focus) but we map competencies to skills the student demonstrated, not skills they failed to show. Confidence: medium because ‘wasn’t fully engaged’ is a subjective teacher judgment — the word ‘fully’ implies some engagement was present, and the teacher does not describe specific disengaged behaviors (e.g., looking away, not responding), leaving room for interpretation."
    },
    {
      "evidence": "after one-on-one support, she understood the concept",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "medium",
      "reasoning": "Type: behavioral_evidence because the teacher describes an observable outcome — the student understanding a concept after receiving one-on-one support. Not emotional_indicator because no feelings are mentioned. Not context_marker because the one-on-one support is part of the student’s learning experience, not just a setting detail. Competencies: none, because comprehension after teacher support is an academic outcome, not a demonstration of an SEL skill. One might consider self_management (persistence) but the text does not indicate the student actively sought help or self-regulated — the support was provided to her. Confidence: medium because ‘understood the concept’ is the teacher’s assessment of internal comprehension — the teacher likely verified this through some observable behavior (correct answers, verbal confirmation), but the specific evidence of understanding is not described in the text."
    },
    {
      "evidence": "She was able to decompose numbers from 2 to 6 by herself",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high",
      "reasoning": "Type: behavioral_evidence because 'was able to decompose numbers from 2 to 6 by herself' describes a specific, observable academic action with a concrete outcome. Not concern_flag because this is a positive achievement. Not context_marker because it describes what the student did, not the setting. Competencies: none, because decomposing numbers is a purely academic skill demonstration without an SEL dimension. One might consider self_management (independent work) but working independently on an assigned task does not by itself demonstrate goal-setting, impulse control, or emotional regulation. Confidence: high because the teacher specifies an exact, measurable action ('decompose numbers from 2 to 6') and confirms it was done independently ('by herself') — there is no ambiguity or teacher interpretation involved."
    },
    {
      "evidence": "eventually became frustrated and started crying, saying she \"can’t do hard things.\"",
      "type": "concern_flag",
      "sel_competencies": [],
      "observation_confidence": "high",
      "reasoning": "Type: concern_flag because the combination of frustration, crying, and a negative self-statement (‘can’t do hard things’) represents an emotional escalation that warrants teacher attention. Not emotional_indicator alone because the broader context (‘tends to get discouraged easily’) frames this as a recurring pattern, not a one-time emotional expression — the severity and pattern together cross the concern threshold. Competencies: none, because the behavior reflects an emotional struggle rather than a demonstrated SEL skill. One might consider self_awareness (she names her difficulty) but ‘can’t do hard things’ is a distressed outburst rather than reflective self-assessment — it expresses frustration, not genuine recognition of a growth area. Confidence: high because the teacher directly observed two concrete behaviors (became frustrated, started crying) and provides a direct quote from the student (‘can’t do hard things’), leaving no ambiguity about what occurred. Signal boundary: the quote spans from the behavioral shift (‘became frustrated’) through the emotional escalation (‘started crying’) to the self-statement (‘can’t do hard things’) because these are a single escalation sequence — splitting them would lose the causal chain that makes this a concern rather than isolated events. Concern threshold: ‘started crying’ and the absolute self-defeating language ‘can’t do hard things’ indicate emotional overwhelm beyond routine frustration; combined with the subsequent sentence’s ‘tends to get discouraged easily’ confirming this is a pattern, the language clearly crosses from a normal struggle into a flaggable concern."
    }
  ]
}
```
