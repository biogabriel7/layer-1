# Layer 1 Evaluation Summary

_Generated 2026-04-16 15:50 — scope: first 50 golden examples (with reasoning audit)_

**50 observations scored · 150 signals extracted · 40 individual / 10 group**

## Results

```text
Scored 50 results (50 golden annotations available)

Dimension                                    Rate   Target    Floor  Result  Detail
--------------------------------------------------------------------------------------------------------------
Evidence Grounding                          98.0%     100%      95%  WARN    147/150 signals
Observation Type                           100.0%     100%      98%  PASS    50/50 observations
Signal Completeness (recall)                92.2%      85%      75%  PASS    118/128 golden signals
No Hallucinated Signals (precision)         78.7%     100%      95%  FAIL    118/150 predicted signals
Type Accuracy                               91.5%      95%      85%  WARN    108/118 matched pairs

Golden-annotated observations scored: 50

Evidence grounding failures (first 20):
  20e745ff1cd3  'George did a great job tying the "coada vacii" knot on his own'
  5a0230aae3d8  'We played a game called "Hocus Pocus, Everybody Focus."'
  9d06e78fbb48  'They also enjoyed creating a model "nose" using condiments of their choice, thoughtfully selectin...'

Reasoning Audit (N=50 observations)
Dimension                                    Rate   Target    Floor  Result  Detail
--------------------------------------------------------------------------------------------------------------
Reasoning matches answer                    90.0%      95%      85%  WARN    135/150 signals

Flagged signals (first 20):
  1cf1f0d5be09  'when it was time to clean up, she refused to help and left her supplies on the table'  → The reasoning justifies concern_flag type and high confidence well, but the S...
  1cf1f0d5be09  'She also told another student that their painting looked ugly, which made the other student cry.'  → The reasoning justifies concern_flag type and high confidence well, but assig...
  201c2991a958  'during PE'  → The reasoning correctly identifies context_marker and no competencies, but 'd...
  20e745ff1cd3  'When it came to the sliding knot, he initially became frustrated and upset when he realized he co...'  → The reasoning justifies merging as a single emotional escalation sequence, bu...
  5970e65ee061  'during lunch'  → The reasoning correctly identifies context_marker and no competencies, but 'd...
  5a0230aae3d8  'at the end they told me that the game was both playful and useful'  → The reasoning classifies this as emotional_indicator because students express...
  904107b72e5b  'Amara chose to write a story about a girl who overcomes her fear of public speaking'  → The reasoning justifies self_awareness by inferring a connection between the ...
  904107b72e5b  'Her narrative included vivid descriptions and dialogue that showed character development'  → The reasoning assigns medium confidence because the teacher mixes observation...
  904107b72e5b  'She voluntarily read her story aloud to the class, which is something she has never done before'  → The self_awareness competency is justified by inferring that Amara 'recognize...
  9d06e78fbb48  'Through discussion, they developed an understanding of the close connection between smell and tas...'  → Reasoning justifies medium confidence via Rule 8 and teacher-assessed compreh...
  b958a068a00e  'the Lower Middle showed that they can collaborate and compete without getting upset'  → The reasoning assigns low confidence citing Rule 9 (capability statement with...
  e2ec6d89548b  'he became frustrated when his teammates suggested changes to his plan and dismissed their ideas w...'  → The reasoning does not adequately justify concern_flag over behavioral_eviden...
  e2ec6d89548b  "By the end of the session, he acknowledged that he should have been more open to others' suggesti..."  → The reasoning justifies self_awareness but does not address why social_awaren...
  e69828862d4e  'Andrei experienced some difficulty during Art'  → The reasoning calls this a context_marker because it 'establishes the setting...
  e69828862d4e  'Through one-on-one support, Andrei was able to re-engage in the activity'  → The reasoning assigns medium confidence partly because of 'was able to' phras...

Golden Comparison (N=50 observations)
  98 total differences  |  model_wrong: 48  golden_wrong: 8  ambiguous: 42
  38 observation(s) with differences — see the Divergent Extractions section for full output comparisons.
```

## Signal Mix

![Signal Type Distribution](charts/signal_mix.svg)

## Observation Confidence

![Observation Confidence Distribution](charts/observation_confidence.svg)

## SEL Competencies

![SEL Competency Frequency](charts/sel_competencies.svg)

## Golden vs Predicted

**Golden vs Predicted Signal Counts (golden-annotated subset)**

|  | Golden |  | Predicted |  |
| :--- | ---: | :--- | ---: | :--- |
| behavioral evidence | 83 | `████████████████████` | 82 | `████████████████████` |
| emotional indicator | 13 | `███` | 17 | `████` |
| context marker | 18 | `████` | 23 | `██████` |
| concern flag | 14 | `███` | 28 | `███████` |

## Concern Flag Rate

![Avg Concern Flags per Observation](charts/concern_flag_average.svg)

## Divergent Extractions

_Top 5 observations where predicted and golden signals diverge most, ranked by the reasoning judge's weighted verdict counts (model_wrong=3, ambiguous=2, golden_wrong=1). Shows the exact predicted and golden outputs side by side._

### Example 1: `63ade372e5b4`

_The model and golden largely agree on signal types, competencies, and confidence levels, with the most notable structural difference being the model's merger of the curiosity judgment and questioning behavior into one signal (where golden splits them per Rule 3's exception). The golden's assignment of responsible_decision_making to the 'best day of school ever' emotional indicator appears to be a rubric error and warrants human review, as self_awareness is the clearly better fit for a student expressing enjoyment._

**Observation** (student_count=1):

> During the outdoor education session at the nature reserve, Kai demonstrated exceptional curiosity by asking questions about every plant species we encountered. He carefully sketched three different leaf shapes in his journal and labeled them correctly. He shared his magnifying glass with a classmate who had forgotten theirs and explained how to use it properly. When we reached the stream crossing, he hesitated but encouraged himself by saying 'I can do this' before stepping across. He then turned around and offered his hand to help the next student across. At the end of the trip, he told me it was the best day of school ever.

**Judge analysis:**

- **MODEL WRONG** — _Rule 3: Observable over evaluative — exception applies only to student's own expressed feeling; but also Rule 2: One signal per evidence unit — the golden split is defensible if curiosity is treated as an observable disposition rather than a teacher judgment._: The model merges 'Kai demonstrated exceptional curiosity' and 'asking questions about every plant species we encountered' into a single behavioral_evidence signal, while golden splits them into two signals: an emotional_indicator ('Kai demonstrated exceptional curiosity') and a behavioral_evidence ('asking questions about every plant species we encountered').
  - _why:_ Rule 3 instructs that when a judgment is paired with a concrete action describing the same moment, extract only the action. The model applied Rule 3 and dropped the evaluative framing. However, the golden treats 'demonstrated exceptional curiosity' as an emotional_indicator — which is debatable since curiosity here is the teacher's label, not a student-expressed feeling. Rule 3's exception applies only when the evaluative phrase reports the student's own expressed feeling.
- **AMBIGUOUS** — _Observation Confidence: high — evidence directly states the behavior describing specific actions grounded in what was directly seen or heard._: The model's signal 1 rates 'asking questions about every plant species we encountered' as medium confidence, while golden rates the equivalent behavioral_evidence signal as high confidence.
  - _why:_ The model reasoned that 'every plant species' is likely hyperbolic and no specific questions are described, warranting medium. However, the rubric's high confidence threshold requires 'specific actions grounded in what was directly seen or heard' — asking questions is a directly observed action, and the scope ('every plant species') is the teacher's direct characterization of what they witnessed, not an inference.
- **AMBIGUOUS** — _SEL Competencies: self_awareness (identifying emotions) vs. self_management (impulse control, self-motivation)._: The model includes self_awareness as a competency for signal 4 (stream crossing self-encouragement), while golden lists only self_management for the equivalent signal.
  - _why:_ The model argued that saying 'I can do this' reflects recognition of one's own hesitation (self_awareness). The golden limits this to self_management (self-regulation strategy). The rubric defines self_awareness as recognizing one's own emotions and thoughts — the self-talk does imply some self-awareness, but the primary demonstrated skill is self-regulation (self_management), making the golden's narrower reading defensible.
- **AMBIGUOUS** — _SEL Competencies: relationship_skills (offer help when needed) vs. social_awareness (perspective-taking, empathy)._: The model includes relationship_skills as a competency for signal 5 (offering hand at stream crossing), while golden lists only social_awareness.
  - _why:_ The model argued that offering physical help demonstrates cooperation and offering help when needed (relationship_skills). The golden limits this to social_awareness (perspective-taking, recognizing another's need). The rubric defines relationship_skills as including 'seek and offer help when needed' — offering a hand to help a peer cross is a direct instance of this sub-skill, making the model's inclusion of relationship_skills defensible.
- **GOLDEN WRONG** — _SEL Competencies: responsible_decision_making (constructive choices, evaluating consequences) — does not fit a student expressing that a day was enjoyable; self_awareness (identifying/expressing emotions) is the better fit._: The model's emotional_indicator for 'he told me it was the best day of school ever' includes self_awareness as the competency, while golden assigns responsible_decision_making.
  - _why:_ The model reasoned that articulating a positive emotional experience demonstrates self_awareness (identifying emotions). The golden assigns responsible_decision_making, which seems difficult to justify from the rubric — the student is expressing enjoyment, not making a constructive choice or evaluating consequences. The rubric defines responsible_decision_making as making constructive choices and evaluating consequences, which does not fit a simple expression of enjoyment.
- **MODEL WRONG** — _Rule 1: Evidence must be verbatim quote from observation — including the full natural sentence boundary is preferable._: The golden includes 'At the end of the trip' as part of the emotional_indicator evidence ('At the end of the trip, he told me it was the best day of school ever'), while the model's evidence omits this contextual prefix ('he told me it was the best day of school ever').
  - _why:_ Minor evidence boundary difference — the model trimmed the temporal context phrase. The golden's inclusion of 'At the end of the trip' is more complete as it preserves the timing context within the evidence quote.
- **MODEL WRONG** — _Rule 1: Evidence must be verbatim quote — preserving the full natural evidence unit including its contextual framing is preferable._: The model's stream crossing signal (signal 4) uses a shorter evidence quote ('he hesitated but encouraged himself by saying 'I can do this' before stepping across') omitting the opening clause 'When we reached the stream crossing,' which golden includes.
  - _why:_ The model trimmed the contextual setup clause. The golden preserves the full sentence including the situational context ('When we reached the stream crossing'), which provides important framing for why hesitation occurred.

**Predicted output (7 signals):**

```json
[
  {
    "evidence": "During the outdoor education session at the nature reserve",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: context_marker because this phrase identifies the setting (outdoor education session) and location (nature reserve) that frame the entire observation — it describes the situation, not a student action or emotion. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: high because the teacher explicitly and unambiguously names the specific event and location."
  },
  {
    "evidence": "Kai demonstrated exceptional curiosity by asking questions about every plant species we encountered",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because asking questions about plant species is an observable action the teacher witnessed. Per Rule 3, the evaluative framing ('demonstrated exceptional curiosity') is paired with a concrete action ('asking questions about every plant species'), so we extract the action. Competencies: none, because asking questions about academic content (plant species) is an intellectual behavior, not a demonstration of an SEL competency. One might consider self_awareness (recognizing curiosity) but the curiosity label is the teacher's interpretation, not the student's self-reflection. Confidence: medium because while asking questions is observable, 'every plant species' is likely hyperbolic and the teacher does not provide specific examples of questions asked, making this somewhat broad."
  },
  {
    "evidence": "He carefully sketched three different leaf shapes in his journal and labeled them correctly",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because sketching and labeling are specific, observable academic actions the teacher directly witnessed. Competencies: none, because sketching and labeling leaf shapes is an academic task without an SEL dimension. One might consider self_management (focus, discipline) but completing an assigned task carefully does not by itself demonstrate goal-setting or emotional regulation. Confidence: high because the teacher specifies exact, measurable details — three leaf shapes, sketched and labeled correctly — leaving no ambiguity."
  },
  {
    "evidence": "He shared his magnifying glass with a classmate who had forgotten theirs and explained how to use it properly",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "social_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because sharing equipment and explaining its use are specific, observable actions the teacher witnessed. Competencies: relationship_skills because sharing a resource and teaching a peer how to use it demonstrates cooperation, offering help, and communication. Social_awareness because noticing a classmate's need (forgotten magnifying glass) and responding to it demonstrates empathy and perspective-taking — Kai recognized the other student's situation and acted on it. Confidence: high because the teacher describes two concrete, specific actions (sharing the magnifying glass, explaining how to use it) with clear context (classmate had forgotten theirs), leaving no ambiguity."
  },
  {
    "evidence": "he hesitated but encouraged himself by saying 'I can do this' before stepping across",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management",
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher directly observed and heard specific actions — hesitation, a self-encouragement statement, and then stepping across. While 'I can do this' expresses an internal state, the primary signal here is the self-regulation strategy (positive self-talk) the student employed to overcome hesitation, making this a behavioral action rather than purely an emotional expression. Competencies: self_management because Kai used a deliberate self-regulation strategy (positive self-talk) to manage his fear/hesitation and motivate himself to act — this demonstrates impulse control and self-motivation. Self_awareness because saying 'I can do this' reflects recognition of his own hesitation and a conscious effort to counter it, showing awareness of his emotional state. Confidence: high because the teacher provides a direct quote ('I can do this'), describes the specific physical context (stream crossing), and notes the sequence of hesitation followed by action — all directly observed with no ambiguity."
  },
  {
    "evidence": "He then turned around and offered his hand to help the next student across",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "social_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because turning around and offering a hand are specific, observable physical actions the teacher witnessed. Competencies: relationship_skills because offering physical help to a peer demonstrates cooperation and offering help when needed. Social_awareness because Kai proactively recognized that the next student might need assistance at the stream crossing — this shows perspective-taking and empathy, anticipating another's need without being asked. Confidence: high because the teacher describes a concrete, specific action (turned around, offered his hand) with clear context (helping the next student across the stream), leaving no ambiguity."
  },
  {
    "evidence": "he told me it was the best day of school ever",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: emotional_indicator because the student directly communicated his feelings about the experience to the teacher — this is a self-reported emotional state (enthusiasm, joy). Not behavioral_evidence because the core content is about how the student felt, not what he did. Competencies: self_awareness because Kai is recognizing and articulating his own positive emotional experience, demonstrating the ability to identify and express his feelings. Confidence: high because this is the student's own reported statement conveyed through direct dialogue ('he told me'), giving the teacher first-hand access to the student's emotional experience with no inference required."
  }
]
```

**Golden output (8 signals):**

```text
"signals": [
    {
      "evidence": "During the outdoor education session at the nature reserve",
      "type": "context_marker",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "Kai demonstrated exceptional curiosity",
      "type": "emotional_indicator",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "asking questions about every plant species we encountered",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "He carefully sketched three different leaf shapes in his journal and labeled them correctly",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "He shared his magnifying glass with a classmate who had forgotten theirs and explained how to use it properly",
      "type": "behavioral_evidence",
      "sel_competencies": ["social_awareness", "relationship_skills"],
      "observation_confidence": "high"
    },
    {
      "evidence": "When we reached the stream crossing, he hesitated but encouraged himself by saying 'I can do this' before stepping across",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "He then turned around and offered his hand to help the next student across",
      "type": "behavioral_evidence",
      "sel_competencies": ["social_awareness"],
      "observation_confidence": "high"
    },
    {
      "evidence": "At the end of the trip, he told me it was the best day of school ever",
      "type": "emotional_indicator",
      "sel_competencies": ["responsible_decision_making"],
      "observation_confidence": "high"
    }
  ]
```

### Example 2: `20e745ff1cd3`

_The model and golden broadly agree on the core signals but diverge on three meaningful issues: (1) the model incorrectly extracts 'showing confidence' as a standalone emotional_indicator rather than treating it as an evaluative judgment paired with the knot-tying action; (2) the model incorrectly merges the emotional reaction and behavioral response into one signal where golden correctly splits them; and (3) the model classifies the re-engagement difficulty as a concern_flag where golden treats it as behavioral_evidence — this last difference is ambiguous and may warrant human review of the golden annotation given the 'even with help' language._

**Observation** (student_count=1):

> George did a great job tying the ""coada vacii"" knot on his own, showing confidence in his ability. When it came to the sliding knot, he initially became frustrated and upset when he realized he couldn't do it by himself. He walked away and said he didn't know how to complete the knot, and even though we discussed the importance of progress and perseverance, George had a hard time coming back to try again, even with help. This is an important learning moment for George, as he is still developing his ability to manage frustration and persist through challenges.

**Judge analysis:**

- **MODEL WRONG** — _Rule 3: Observable over evaluative — teacher judgment paired with a concrete action should yield only the action signal_: Model includes 'showing confidence in his ability' as a separate emotional_indicator signal with self_awareness; golden does not extract this as a separate signal at all.
  - _why:_ Rule 3 (Observable over evaluative): 'showing confidence' is a teacher judgment paired with the concrete action of tying the knot independently. The rubric says to extract the action rather than the evaluative phrase. Golden correctly omits it as a standalone signal.
- **AMBIGUOUS** — _SEL Competencies: self_management — self-discipline, self-motivation sub-skills_: Model assigns no SEL competencies to the knot-tying behavioral_evidence signal; golden assigns self_management.
  - _why:_ Golden appears to interpret independent task completion ('on his own') as demonstrating self_management (self-discipline, self-motivation). The model's reasoning argues that completing an assigned task independently doesn't inherently demonstrate self_management sub-skills. This is a borderline judgment call.
- **MODEL WRONG** — _Rule 2: One signal per evidence unit — merging hides a distinct second signal; Rule 5: Mixed observations extract both_: Model merges the emotional reaction ('became frustrated and upset') and the behavioral response ('walked away and said he didn't know') into one emotional_indicator signal; golden splits them into two separate signals — one emotional_indicator and one behavioral_evidence.
  - _why:_ Rule 2 (One signal per evidence unit): the two sentences describe distinct signal types — an emotional state and a behavioral action. Golden correctly splits them because merging hides a distinct behavioral signal. The model's merge under emotional_indicator misclassifies the behavioral content of the second sentence.
- **MODEL WRONG** — _SEL Competencies: self_awareness — accurately recognizing one's own emotions/strengths; distressed outburst differs from reflective self-assessment_: Model assigns self_awareness to the merged frustration/walking-away signal; golden assigns no SEL competencies to either the emotional_indicator or the behavioral_evidence split signals.
  - _why:_ The model interprets verbalizing inability ('said he didn't know how to complete the knot') as self_awareness (recognizing one's own skill gap). Golden treats this as a distressed behavioral/emotional response without a demonstrated SEL competency. Given that the verbalization is under distress rather than reflective self-assessment, golden's approach aligns better with the rubric's definition of self_awareness.
- **AMBIGUOUS** — _Rule: concern_flag requires language indicating pattern/risk — 'had a hard time' may not clearly cross the threshold; confidence level also differs_: Model classifies 'George had a hard time coming back to try again, even with help' as concern_flag with self_management and high confidence; golden classifies it as behavioral_evidence with no SEL competencies and medium confidence.
  - _why:_ The concern_flag vs. behavioral_evidence distinction: the rubric requires language indicating a pattern, risk, or regression. 'Had a hard time coming back to try again, even with help' describes a specific observed behavior but the phrase 'even with help' could indicate a notable difficulty. However, the rubric's concern_flag threshold requires words like 'repeatedly', 'refuses', 'can't control' — 'had a hard time' is closer to a struggle than a flaggable pattern. Golden's medium confidence (vs. model's high) is also defensible since 'had a hard time' is somewhat evaluative without specifying exactly what the teacher observed.
- **AMBIGUOUS** — _What NOT to Extract: teacher judgments about potential not grounded in a witnessed action; Rule 9: capability statements capped at low confidence_: Golden extracts 'he is still developing his ability to manage frustration and persist through challenges' as a separate behavioral_evidence signal with low confidence; model does not extract this as a standalone signal but uses it as supporting context for the concern_flag.
  - _why:_ The model treats this sentence as teacher framing/reflection rather than extractable evidence. However, the rubric's 'What NOT to Extract' section excludes 'teacher reflections on lesson value or takeaways' — this sentence is the teacher's assessment of the student's developmental stage, which is closer to a capability statement (Rule 9) or teacher judgment. Golden's extraction as low-confidence behavioral_evidence is defensible but the sentence reads more like a teacher interpretation than a witnessed action.

**Predicted output (4 signals):**

```json
[
  {
    "evidence": "George did a great job tying the \"coada vacii\" knot on his own",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes a specific, observable action — George successfully tying a particular knot independently. Not emotional_indicator because the action is physical, not affective. Competencies: none, because tying a knot is a practical/motor skill demonstration without an inherent SEL dimension. One might consider self_management (independent task completion), but completing an assigned task independently does not by itself demonstrate goal-setting, impulse control, or emotional regulation. Confidence: high because the teacher specifies the exact knot ('coada vacii'), confirms it was done independently ('on his own'), and directly witnessed the action — concrete and unambiguous."
  },
  {
    "evidence": "showing confidence in his ability",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: emotional_indicator because 'showing confidence' describes an observed disposition/affect — the teacher perceived confidence in the student's demeanor. Not behavioral_evidence because this is about the student's emotional state, not a discrete action. Competencies: self_awareness because confidence in one's ability reflects self-efficacy and recognition of one's own strengths. Confidence: medium because 'showing confidence' is the teacher's interpretation of the student's demeanor — the teacher likely observed body language or attitude cues, but the specific observable indicators are not described."
  },
  {
    "evidence": "When it came to the sliding knot, he initially became frustrated and upset when he realized he couldn't do it by himself. He walked away and said he didn't know how to complete the knot",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: emotional_indicator because the core content is the student's emotional state — 'became frustrated and upset' — accompanied by observable behavioral manifestations (walking away, verbal statement). Not purely behavioral_evidence because the emotional reaction is the central element, with the actions serving as expressions of that emotion. Competencies: self_awareness because the student verbalized his limitation ('said he didn't know how to complete the knot'), demonstrating recognition of his own skill gap — even though the expression was distressed, he accurately identified what he couldn't do. Confidence: high because the teacher directly observed concrete behaviors (walked away) and reports the student's own words ('said he didn't know how to complete the knot'), providing specific, unambiguous evidence. Signal boundary: these two sentences are merged because they describe a single escalation sequence — the emotional reaction (frustrated and upset) leading to the behavioral response (walked away and verbalized) — splitting them would lose the causal chain."
  },
  {
    "evidence": "George had a hard time coming back to try again, even with help",
    "type": "concern_flag",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: concern_flag because the teacher describes the student's inability to re-engage with the task even when support was offered ('even with help'), indicating a difficulty with frustration tolerance and persistence that goes beyond a routine struggle. The broader context of the observation — particularly the next sentence confirming 'he is still developing his ability to manage frustration and persist through challenges' — frames this as an ongoing developmental concern. Competencies: self_management because the inability to return to a challenging task after frustration directly relates to emotional regulation, impulse control, and persistence — core self_management sub-skills. Confidence: high because the teacher directly observed the student's failure to re-engage and specifies the conditions ('even with help'), providing concrete, unambiguous evidence. Concern threshold: 'had a hard time coming back to try again, even with help' crosses from routine struggle into flaggable concern because the phrase 'even with help' indicates that adult support was insufficient to help the student re-engage — this is not a case of needing a bit of encouragement but rather a significant difficulty with emotional recovery. The teacher's subsequent framing ('still developing his ability to manage frustration') confirms this is a recognized pattern, not an isolated incident."
  }
]
```

**Golden output (5 signals):**

```text
"signals": [
    {
      "evidence": "tying the ""coada vacii"" knot on his own",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "When it came to the sliding knot, he initially became frustrated and upset when he realized he couldn’t do it by himself",
      "type": "emotional_indicator",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "He walked away and said he didn’t know how to complete the knot",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "George had a hard time coming back to try again, even with help",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "medium"
    },
    {
      "evidence": "he is still developing his ability to manage frustration and persist through challenges",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "low"
    }
  ]
```

### Example 3: `904107b72e5b`

_The model and golden largely agree on signal types, evidence boundaries, and confidence levels, with the main disagreements centered on SEL competency mapping. The model over-infers self_awareness and self_management from implicit cues (story topic choice, voluntary action) where the rubric requires explicit evidence, while the golden over-maps social_awareness and responsible_decision_making onto the pride statement (Signal 6) without textual support — this golden annotation warrants human review._

**Observation** (student_count=1):

> In today's creative writing workshop, Amara chose to write a story about a girl who overcomes her fear of public speaking. She spent extra time planning her story structure before writing. Her narrative included vivid descriptions and dialogue that showed character development. She voluntarily read her story aloud to the class, which is something she has never done before. After reading, she accepted feedback from her peers gracefully and even thanked a classmate who pointed out a spelling error. She told me she felt proud of herself for reading out loud.

**Judge analysis:**

- **MODEL WRONG** — _Rule 4: No inference beyond text_: Signal 1 (story topic choice): model assigns self_awareness; golden assigns no SEL competencies. The model infers that Amara chose the topic because it mirrors her own fear, but the text does not state this connection.
  - _why:_ Rule 4 (No inference beyond text) — the model inferred a personal-reflection motive from the story topic, which is not explicitly stated. The rubric requires extracting only what the teacher explicitly wrote.
- **MODEL WRONG** — _Observation Confidence: high vs. medium — specific observable qualities of a product vs. vague generalities_: Signal 3 (narrative quality): model assigns medium confidence; golden assigns high confidence. The model treats 'vivid descriptions' and 'showed character development' as evaluative judgments, while golden treats them as directly observable qualities of the written product.
  - _why:_ Confidence rubric boundary — 'vivid descriptions' and 'showed character development' are qualitative assessments of a concrete artifact (the written story), which the rubric's high-confidence definition covers as 'specific actions grounded in what was directly seen.' The model over-applied the medium-confidence criterion for mixing observation with opinion.
- **MODEL WRONG** — _Rule 4: No inference beyond text_: Signal 4 (reading aloud): model assigns self_management and self_awareness; golden assigns no SEL competencies. The model infers internal motivation and self-recognition of a personal challenge, neither of which is explicitly stated.
  - _why:_ Rule 4 (No inference beyond text) — 'voluntarily' indicates the action was self-initiated, but the rubric requires explicit evidence of SEL competency demonstration, not inference from the word 'voluntarily' or from the historical note 'never done before.'
- **AMBIGUOUS** — _SEL Competencies: self_awareness, social_awareness, self_management mapping_: Signal 5 (accepting feedback): model assigns relationship_skills and self_management; golden assigns self_awareness, social_awareness, and relationship_skills. The model omits self_awareness and social_awareness while adding self_management.
  - _why:_ Competency mapping disagreement — golden sees accepting feedback gracefully as requiring self_awareness (recognizing one's own work's limitations) and social_awareness (understanding others' perspectives/feedback), while the model focuses on emotional regulation (self_management). The golden's inclusion of social_awareness for accepting peer feedback is debatable; self_management for graceful acceptance is also a reasonable read.
- **AMBIGUOUS** — _Rule 1: Evidence must be verbatim quote from observation_: Signal 5 evidence boundary: model uses 'she accepted feedback...' (omitting 'After reading,'); golden includes 'After reading, she accepted feedback...' The model drops the temporal connector.
  - _why:_ Minor evidence boundary difference — 'After reading,' is a temporal context phrase. The rubric requires verbatim quotes; dropping it slightly changes the evidence unit but does not materially affect classification.
- **GOLDEN WRONG** — _Rule 4: No inference beyond text; SEL Competencies — social_awareness requires perspective-taking/empathy evidence, responsible_decision_making requires evaluating consequences or choices_: Signal 6 (felt proud): model assigns only self_awareness; golden assigns self_awareness, social_awareness, and responsible_decision_making. The golden's addition of social_awareness and responsible_decision_making to a simple self-reported pride statement is not clearly supported.
  - _why:_ Golden appears to over-map competencies — 'She told me she felt proud of herself for reading out loud' is a self-reported emotional state. There is no explicit evidence of perspective-taking (social_awareness) or decision-making evaluation (responsible_decision_making) in this statement. The model's single self_awareness mapping is better supported by the rubric.

**Predicted output (7 signals):**

```json
[
  {
    "evidence": "In today's creative writing workshop",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: context_marker because this phrase identifies the setting and activity framing the observation — it describes the situation, not a student action or emotion. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: high because the teacher explicitly and unambiguously names the specific event and timeframe."
  },
  {
    "evidence": "Amara chose to write a story about a girl who overcomes her fear of public speaking",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes a specific, observable creative choice Amara made — selecting a particular story topic. Competencies: self_awareness because the chosen theme (overcoming fear of public speaking) directly mirrors what Amara herself later does (reading aloud for the first time), suggesting she is reflecting on her own experiences and emotions through her writing. Confidence: high because the teacher directly observed the specific topic Amara chose, leaving no ambiguity about the action."
  },
  {
    "evidence": "She spent extra time planning her story structure before writing",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher observed a specific action — Amara deliberately spending additional time on planning before writing. Competencies: self_management because taking extra time to plan before executing demonstrates organizational skills, self-discipline, and goal-directed behavior. Confidence: high because the teacher directly witnessed the student spending extra time on planning, describing a concrete and specific behavior."
  },
  {
    "evidence": "Her narrative included vivid descriptions and dialogue that showed character development",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because the teacher describes observable qualities of the student's written work — vivid descriptions, dialogue, and character development. Competencies: none, because these are academic writing skills rather than demonstrations of SEL competencies. One might consider social_awareness (perspective-taking through character development), but the evidence describes a writing technique, not the student demonstrating empathy or understanding of others' perspectives in a social context. Confidence: medium because 'vivid descriptions' and 'showed character development' are the teacher's qualitative assessments of the writing — they describe the product but mix observation with evaluative judgment without providing specific examples from the text."
  },
  {
    "evidence": "She voluntarily read her story aloud to the class, which is something she has never done before",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management",
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher directly witnessed a specific, observable action — Amara voluntarily reading aloud to the class. Competencies: self_management because voluntarily doing something she has never done before demonstrates self-motivation and overcoming internal resistance; self_awareness because the teacher's note that 'she has never done before' implies Amara recognized this was a personal challenge and chose to push past it, reflecting awareness of her own limitations and growth. Confidence: high because the teacher directly observed the action ('read her story aloud to the class'), specifies it was voluntary, and provides concrete historical context ('never done before'), making this highly specific and unambiguous."
  },
  {
    "evidence": "she accepted feedback from her peers gracefully and even thanked a classmate who pointed out a spelling error",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes specific, observable actions — accepting feedback and thanking a classmate. Competencies: relationship_skills because accepting peer feedback and thanking a classmate demonstrates healthy communication, social engagement, and constructive interaction with peers; self_management because accepting criticism gracefully requires emotional regulation and impulse control. Confidence: high because the teacher describes two concrete, specific actions (accepting feedback, thanking a classmate) with a specific detail (the spelling error), grounded in direct observation. Signal boundary: the two actions are kept as one unit because they describe a single feedback-receiving moment — the acceptance and the thanking are part of the same interaction sequence, and splitting them would lose the context that the thanking was in response to critical feedback."
  },
  {
    "evidence": "She told me she felt proud of herself for reading out loud",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: emotional_indicator because the student directly communicated her emotional state — feeling proud — to the teacher. Not behavioral_evidence because the core content is about how the student felt, not what she did. Competencies: self_awareness because Amara is recognizing and articulating her own emotional response (pride) and connecting it to a specific accomplishment (reading out loud), demonstrating the ability to identify her emotions and assess her own growth. Confidence: high because these are the student's own reported words conveyed through direct dialogue ('She told me she felt proud'), giving the teacher first-hand access to the student's emotional experience with no inference required."
  }
]
```

**Golden output (7 signals):**

```text
"signals": [
    {
      "evidence": "In today's creative writing workshop",
      "type": "context_marker",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "Amara chose to write a story about a girl who overcomes her fear of public speaking",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "She spent extra time planning her story structure before writing",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "Her narrative included vivid descriptions and dialogue that showed character development",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "She voluntarily read her story aloud to the class, which is something she has never done before",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "After reading, she accepted feedback from her peers gracefully and even thanked a classmate who pointed out a spelling error",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_awareness", "social_awareness", "relationship_skills"],
      "observation_confidence": "high"
    },
    {
      "evidence": "She told me she felt proud of herself for reading out loud",
      "type": "emotional_indicator",
      "sel_competencies": ["self_awareness", "social_awareness", "responsible_decision_making"],
      "observation_confidence": "high"
    }
  ]
```

### Example 4: `98f965078775`

_The model and golden broadly agree on signal types and evidence boundaries, but the model over-assigns SEL competencies (adding self_management to turn-taking, responsible_decision_making to democratic discussion, and omitting social_awareness from the conflict-resolution signal) and consistently applies Rule 8 to cap confidence at medium for all group signals where the golden rates two of three as high. The competency disagreements warrant a human review of the golden to confirm whether social_awareness and responsible_decision_making should be included on the conflict-resolution signal, as the rubric reasonably supports the golden's broader mapping there._

**Observation** (student_count=6):

> The crew worked together on a mural project. They discussed color choices democratically and took turns painting different sections. When one member accidentally smudged another's section, they resolved it calmly by offering to help fix it.

**Judge analysis:**

- **AMBIGUOUS** — _Signal Types: context_marker — setting, conditions, or social configuration that frames the observation_: The model extracted a context_marker signal for 'The crew worked together on a mural project.' but the golden annotation does not include this signal at all.
  - _why:_ The rubric supports extracting context markers for setting/activity framing, so the model's extraction is defensible. The golden may have omitted it as low-value, but the rubric does not exclude it.
- **MODEL WRONG** — _SEL Competencies: self_management — impulse control, self-discipline; relationship_skills — cooperation, teamwork_: For 'took turns painting different sections', the model assigns self_management alongside relationship_skills, but the golden assigns only relationship_skills.
  - _why:_ The model argues turn-taking requires impulse control (self_management), but the rubric's self_management sub-skills (impulse control, stress management, self-discipline, self-motivation, goal setting) are a stretch for a cooperative turn-taking norm in a group activity — the behavior is more naturally a relationship/teamwork skill than an individual self-regulation act.
- **AMBIGUOUS** — _Rule 8: Group observations with unnamed actors — confidence capped at medium_: For 'took turns painting different sections', the model assigns medium confidence (citing Rule 8 for unnamed actors) while the golden assigns high confidence.
  - _why:_ Rule 8 caps confidence at medium for unnamed actors, but the observation has a student_count of 6 and the action is attributed to the whole group ('they'), which is a named collective. The golden may treat the group as the attributable subject, making the action directly observable at high confidence. Rule 8 is most clearly triggered when a subgroup is unnamed within a larger group, not when the entire group performs an action together.
- **MODEL WRONG** — _SEL Competencies: social_awareness — empathy, perspective-taking; responsible_decision_making — solving problems, considering well-being of others_: For the smudging/resolution signal, the model assigns medium confidence while the golden assigns high confidence, and the model omits social_awareness and responsible_decision_making that the golden includes.
  - _why:_ On confidence: same Rule 8 ambiguity as above — the golden treats the group action as directly observable. On competencies: the golden includes social_awareness (the offer to help reflects perspective-taking/empathy toward the affected peer) and responsible_decision_making (choosing a constructive resolution). The model explicitly excluded social_awareness arguing the evidence shows action not perspective-taking, but the rubric's social_awareness includes empathy and the offer to help fix the smudge is a concrete empathic act. Responsible_decision_making (evaluating consequences, considering well-being of others) also fits the deliberate choice to resolve calmly rather than escalate.
- **MODEL WRONG** — _SEL Competencies: responsible_decision_making — constructive choices about personal behavior; relationship_skills — communication, cooperation, teamwork_: For 'They discussed color choices democratically', the model includes responsible_decision_making in addition to relationship_skills, but the golden assigns only relationship_skills.
  - _why:_ The model argues democratic group decision-making maps to responsible_decision_making (analyzing situations, making constructive choices). However, the evidence is a brief, vague description of a group discussion process; the rubric's responsible_decision_making focuses on individual constructive choices about personal behavior and social interactions based on ethical standards. A group discussion process is more naturally relationship_skills (communication, cooperation). The golden's narrower mapping is more defensible.

**Predicted output (4 signals):**

```json
[
  {
    "evidence": "The crew worked together on a mural project.",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: context_marker because this sentence establishes the setting and activity (a mural project) that frames the rest of the observation — it describes the situation, not a specific student action or emotion. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: high because the teacher explicitly and unambiguously names the specific activity."
  },
  {
    "evidence": "They discussed color choices democratically",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "responsible_decision_making"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because 'discussed color choices democratically' describes an observable group action — the students engaged in a collaborative decision-making process. Not emotional_indicator because no feelings are described. Competencies: relationship_skills because democratic discussion demonstrates communication, cooperation, and teamwork; responsible_decision_making because making group decisions about color choices through democratic process reflects analyzing situations and making constructive choices that consider the well-being of the group. Confidence: medium because this is a group observation with unnamed actors (student_count is 6 but no individuals are named), capping confidence at medium per Rule 8. Additionally, 'democratically' is somewhat interpretive — the teacher does not describe the specific behaviors that constituted democratic discussion (e.g., voting, each person suggesting a color)."
  },
  {
    "evidence": "took turns painting different sections",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management",
      "relationship_skills"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because 'took turns painting different sections' describes a specific, observable cooperative action. Competencies: self_management because taking turns requires impulse control and self-discipline — waiting for one's turn rather than painting wherever one wants; relationship_skills because turn-taking is a core cooperation and teamwork skill in a group setting. Confidence: medium because this is a group observation with unnamed actors, capping confidence at medium per Rule 8. The action itself ('took turns') is concrete and observable, but it cannot be attributed to any specific student."
  },
  {
    "evidence": "When one member accidentally smudged another's section, they resolved it calmly by offering to help fix it.",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management",
      "relationship_skills"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because the teacher describes a specific observable sequence: a conflict arose (accidental smudging) and the students resolved it through a concrete action (offering to help fix it). Not emotional_indicator because 'calmly' describes the manner of the action rather than a reported or expressed emotional state. Competencies: self_management because resolving the situation 'calmly' demonstrates emotional regulation and impulse control in a moment that could have triggered frustration or blame; relationship_skills because offering to help fix the smudge demonstrates conflict resolution, cooperation, and prosocial behavior. Not social_awareness because while empathy may underlie the offer to help, the evidence describes the action (offering help) rather than perspective-taking or empathizing. Confidence: medium because the actors are unnamed ('one member', 'they'), capping confidence at medium per Rule 8. The behavior itself is specific and concrete, but it cannot be attributed to identified students. Signal boundary: the entire sentence is kept as one unit because the conflict trigger ('accidentally smudged another's section') and the resolution ('resolved it calmly by offering to help fix it') form a single causal sequence — splitting them would lose the conflict-resolution structure that gives the signal its meaning."
  }
]
```

**Golden output (3 signals):**

```text
"signals": [
    {
      "evidence": "They discussed color choices democratically",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "observation_confidence": "medium"
    },
    {
      "evidence": "took turns painting different sections",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "observation_confidence": "high"
    },
    {
      "evidence": "When one member accidentally smudged another's section, they resolved it calmly by offering to help fix it.",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills", "social_awareness", "responsible_decision_making"],
      "observation_confidence": "high"
    }
  ]
```

### Example 5: `e69828862d4e`

_The model and golden largely agree on the core signals and their classifications, with the main divergences being: an extra context_marker signal the model extracted that golden omits, a missing low-confidence capability signal the golden includes, a competency disagreement on the emotional expression signal (self_management omitted by model), a confidence disagreement on re-engagement (medium vs. high), and an evidence boundary/competency difference on the ownership signal. The most clear-cut error is the model retaining the evaluative phrase 'gradually took more ownership' in the evidence and adding responsible_decision_making; the golden's trimming to the concrete actions is better supported by Rule 3. The missing final signal and the self_management omission on signal_index 2 warrant a human review of the golden annotation to confirm intent._

**Observation** (student_count=1):

> Andrei experienced some difficulty during Art and chose to take a break outside, where he was able to express that he was feeling overwhelmed. He shared that he sometimes finds it hard to manage when many things are happening around him and that he worries about making mistakes. Through one-on-one support, Andrei was able to re-engage in the activity and gradually took more ownership of his choices-selecting his own colors and deciding which shapes to focus on in his drawing. His statement, ""Once I finish this drawing, I have three more shapes,"" showed a shift toward planning and a growing sense of self-direction. Andrei is developing emotional awareness and learning to build trust in his own decision-making.

**Judge analysis:**

- **MODEL WRONG** — _Signal Types: context_marker — 'Setting, conditions, timeframe, constraints, or social configuration that frames the observation. Context markers describe the situation, not the student directly.'_: Model extracted an extra signal for 'Andrei experienced some difficulty during Art' classified as context_marker; golden does not include this signal at all.
  - _why:_ The phrase describes a student's state rather than a pure setting/framing detail. The rubric defines context_marker as setting, conditions, timeframe, or social configuration — a student's difficulty is more behavioral. The golden correctly omits it as it adds little beyond framing already captured by subsequent signals.
- **AMBIGUOUS** — _SEL Competencies: self_management — 'successfully regulate one's emotions… managing stress'; self_awareness — 'accurately recognize one's own emotions'_: Model's signal_index 2 uses evidence 'he was able to express that he was feeling overwhelmed' while golden uses 'where he was able to express that he was feeling overwhelmed' (includes 'where'); more importantly, model assigns only self_awareness while golden assigns both self_awareness and self_management.
  - _why:_ The act of expressing one's overwhelmed state — especially after choosing to take a break — can be seen as a self-management strategy (stress management, seeking support). The golden annotator included self_management because articulating one's emotional state to regulate it is a self-management sub-skill. The model's reasoning only addresses self_awareness without considering the regulatory function of the expression.
- **AMBIGUOUS** — _Rule 9: Capability vs. observed action — 'Statements about what a student can do… describe potential, not witnessed events… confidence is capped at low unless paired with a specific witnessed instance'_: Model's signal_index 4 assigns medium confidence to 'Through one-on-one support, Andrei was able to re-engage in the activity' while golden assigns high confidence.
  - _why:_ The model applied Rule 9 (capability language — 'was able to') to cap confidence at medium, but the golden treats re-engagement as a directly observed outcome. The teacher witnessed the re-engagement happening, making it an observed event rather than a capability statement; 'was able to' here describes what occurred, not a general potential.
- **MODEL WRONG** — _Rule 3: Observable over evaluative — 'When the teacher pairs a judgment with a concrete action describing the same moment, extract only the action'; responsible_decision_making — 'constructive choices about personal behavior and social interactions based on ethical standards, safety concerns, and social norms'_: Model's signal_index 5 uses evidence 'gradually took more ownership of his choices-selecting his own colors and deciding which shapes to focus on in his drawing' and assigns both self_management and responsible_decision_making; golden uses only 'selecting his own colors and deciding which shapes to focus on in his drawing' and assigns only self_management.
  - _why:_ The golden trims the evaluative phrase 'gradually took more ownership of his choices' per Rule 3 (observable over evaluative — teacher judgment paired with concrete action), keeping only the concrete actions. The model retains the evaluative framing. On competencies, the golden excludes responsible_decision_making, likely because selecting art materials is a low-stakes personal choice rather than a decision involving ethical standards, safety, or social norms as the rubric describes.
- **AMBIGUOUS** — _What NOT to Extract: 'Teacher judgments about character, personality, or potential not grounded in a witnessed action'; Rule 9: capability statements extractable but capped at low_: Golden includes a signal for 'Andrei is developing emotional awareness and learning to build trust in his own decision-making' (low confidence, behavioral_evidence, self_management + self_awareness) that the model did not extract.
  - _why:_ The model likely treated this as a teacher judgment/interpretation about the student's trajectory rather than an observable behavior, consistent with 'What NOT to Extract: Teacher judgments about character, personality, or potential not grounded in a witnessed action.' However, the golden extracted it at low confidence as a capability statement. The rubric's 'What NOT to Extract' section and Rule 9 both apply here, making the model's omission defensible.

**Predicted output (7 signals):**

```json
[
  {
    "evidence": "Andrei experienced some difficulty during Art",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "medium",
    "reasoning": "Type: context_marker because this establishes the setting (Art class) and the general condition (difficulty) that frames the rest of the observation — it describes the situation, not a specific student action or emotion. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: medium because 'experienced some difficulty' is vague — the teacher does not specify what the difficulty was (sensory, academic, social), leaving room for interpretation."
  },
  {
    "evidence": "chose to take a break outside",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because 'chose to take a break outside' is a specific, observable action the teacher witnessed. Competencies: self_management because the student made a deliberate choice to remove himself from a challenging situation as a self-regulation strategy — this reflects impulse control and stress management. Confidence: high because the teacher describes a concrete, unambiguous action with a clear decision ('chose to') and specific location ('outside')."
  },
  {
    "evidence": "he was able to express that he was feeling overwhelmed",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: emotional_indicator because the student expressed his own emotional state — feeling overwhelmed. This is a self-reported emotion, not just a teacher inference. Competencies: self_awareness because the student identified and articulated his own emotional state ('feeling overwhelmed'), demonstrating the ability to recognize and name his feelings. Confidence: high because the teacher reports the student's own expressed feeling, providing direct evidence of the emotional state with no ambiguity."
  },
  {
    "evidence": "He shared that he sometimes finds it hard to manage when many things are happening around him and that he worries about making mistakes",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: emotional_indicator because the student is sharing his internal emotional experiences — difficulty managing stimulation and worry about mistakes. These are self-reported feelings and reflections. Competencies: self_awareness because the student demonstrates the ability to recognize and articulate his own emotional triggers ('many things happening around him') and a specific worry ('making mistakes'), showing accurate self-perception and identification of emotions. Confidence: high because the teacher reports the student's own words ('He shared that...'), providing direct first-person evidence of his emotional experience. Signal boundary: the two parts (difficulty managing stimulation and worry about mistakes) are kept together because they were shared in the same reflective moment and both describe the student's self-reported internal experience — splitting would fragment a single act of self-disclosure."
  },
  {
    "evidence": "Through one-on-one support, Andrei was able to re-engage in the activity",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because re-engaging in the activity is an observable action. Competencies: self_management because the student regulated his emotional state sufficiently to return to the task, demonstrating stress management and self-motivation — though with teacher support. Confidence: medium because 're-engage in the activity' is somewhat general (the teacher doesn't describe what re-engagement looked like specifically), and the 'was able to' phrasing describes capability rather than a precisely witnessed moment."
  },
  {
    "evidence": "gradually took more ownership of his choices-selecting his own colors and deciding which shapes to focus on in his drawing",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management",
      "responsible_decision_making"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes specific, observable actions — selecting colors and deciding on shapes. Competencies: self_management because taking ownership of choices and making independent decisions about his work reflects self-motivation and self-direction; responsible_decision_making because the student is making constructive choices about his own work, evaluating options (colors, shapes), and acting on them. Confidence: high because the teacher provides concrete, specific examples of the actions ('selecting his own colors and deciding which shapes to focus on'), leaving no ambiguity about what was observed."
  },
  {
    "evidence": "\"Once I finish this drawing, I have three more shapes\"",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because this is a direct quote from the student that demonstrates a specific cognitive action — planning and sequencing his work. Competencies: self_management because the statement shows goal-setting and planning — the student is organizing his work by identifying what comes next after the current task, reflecting self-direction and organizational skills. Confidence: high because this is a verbatim quote from the student, providing unambiguous evidence of his planning behavior."
  }
]
```

**Golden output (7 signals):**

```text
"signals": [
    {
      "evidence": "chose to take a break outside",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "where he was able to express that he was feeling overwhelmed",
      "type": "emotional_indicator",
      "sel_competencies": ["self_awareness", "self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "He shared that he sometimes finds it hard to manage when many things are happening around him and that he worries about making mistakes",
      "type": "emotional_indicator",
      "sel_competencies": ["self_awareness"],
      "observation_confidence": "high"
    },
    {
      "evidence": "Through one-on-one support, Andrei was able to re-engage in the activity",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "selecting his own colors and deciding which shapes to focus on in his drawing",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": """Once I finish this drawing, I have three more shapes,""",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "Andrei is developing emotional awareness and learning to build trust in his own decision-making",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management", "self_awareness"],
      "observation_confidence": "low"
    }
  ]
```

_...and 33 more observations with differences._
