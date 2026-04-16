# Layer 1 Evaluation Summary

_Generated 2026-04-16 13:57 — scope: all 50 results (with reasoning audit)_

**50 observations scored · 149 signals extracted · 40 individual / 10 group**

## Results

```text
Scored 50 results (50 golden annotations available)

Dimension                                    Rate   Target    Floor  Result  Detail
--------------------------------------------------------------------------------------------------------------
Evidence Grounding                          98.0%     100%      95%  WARN    146/149 signals
Observation Type                           100.0%     100%      98%  PASS    50/50 observations
Signal Completeness (recall)                91.4%      85%      75%  PASS    117/128 golden signals
No Hallucinated Signals (precision)         78.5%     100%      95%  FAIL    117/149 predicted signals
Type Accuracy                               90.6%      95%      85%  WARN    106/117 matched pairs

Golden-annotated observations scored: 50

Evidence grounding failures (first 20):
  20e745ff1cd3  'George did a great job tying the "coada vacii" knot on his own'
  5a0230aae3d8  'We played a game called "Hocus Pocus, Everybody Focus."'
  9d06e78fbb48  'They also enjoyed creating a model "nose" using condiments of their choice, thoughtfully selectin...'

Reasoning Audit (N=50 observations)
Dimension                                    Rate   Target    Floor  Result  Detail
--------------------------------------------------------------------------------------------------------------
Reasoning matches answer                    93.3%      95%      85%  WARN    139/149 signals

Flagged signals (first 20):
  1cf1f0d5be09  'when it was time to clean up, she refused to help and left her supplies on the table'  → The reasoning justifies concern_flag and high confidence well, but fails to j...
  1cf1f0d5be09  'She also told another student that their painting looked ugly, which made the other student cry.'  → The reasoning justifies concern_flag and high confidence well, but assigning ...
  4046fac0b16f  'They remained fully present, enthusiastic, and eager to delve deeper into their mathematical dis'  → The reasoning justifies medium confidence via Rule 8 (group observation cap),...
  5970e65ee061  'during lunch'  → The context_marker signal is redundant — 'during lunch' is already embedded w...
  885ee079d72b  'Refused to participate in any group activities again today.'  → The reasoning correctly justifies concern_flag, high confidence, and the conc...
  904107b72e5b  'Amara chose to write a story about a girl who overcomes her fear of public speaking'  → The reasoning justifies self_awareness by inferring a connection between the ...
  904107b72e5b  'Her narrative included vivid descriptions and dialogue that showed character development'  → The reasoning justifies medium confidence by noting the teacher's evaluative ...
  904107b72e5b  'She voluntarily read her story aloud to the class, which is something she has never done before'  → The reasoning attributes self_awareness partly by inferring that Amara 'recog...
  b958a068a00e  'the Lower Middle showed that they can collaborate and compete without getting upset'  → The reasoning assigns low confidence citing Rule 9 (capability statement with...
  e2ec6d89548b  'he became frustrated when his teammates suggested changes to his plan and dismissed their ideas w...'  → The reasoning classifies this as behavioral_evidence but the evidence contain...

Golden Comparison (N=50 observations)
  100 total differences  |  model_wrong: 46  golden_wrong: 14  ambiguous: 40
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
| behavioral evidence | 83 | `████████████████████` | 83 | `████████████████████` |
| emotional indicator | 13 | `███` | 16 | `████` |
| context marker | 18 | `████` | 22 | `█████` |
| concern flag | 14 | `███` | 28 | `███████` |

## Divergent Extractions

_Top observations where predicted and golden signals diverge most, ranked by the reasoning judge's weighted verdict counts (model_wrong=3, ambiguous=2, golden_wrong=1)._

### Example 1: `20e745ff1cd3`

_The model and golden agree on the core knot-tying behavioral evidence and its high confidence, but diverge significantly on signal splitting, type classification, and SEL competency assignment. Key errors include: extracting the evaluative 'showing confidence' phrase as a standalone signal (violating Rule 3), merging the emotional reaction and behavioral response into one behavioral_evidence signal instead of splitting by type, assigning self_awareness to a distressed inability statement, and assigning self_management to a deficit rather than a demonstrated skill. The concern_flag vs. behavioral_evidence disagreement on the final evidence block is genuinely ambiguous and warrants human review of the golden annotation._

**Observation** (student_count=1):

> George did a great job tying the ""coada vacii"" knot on his own, showing confidence in his ability. When it came to the sliding knot, he initially became frustrated and upset when he realized he couldn't do it by himself. He walked away and said he didn't know how to complete the knot, and even though we discussed the importance of progress and perseverance, George had a hard time coming back to try again, even with help. This is an important learning moment for George, as he is still developing his ability to manage frustration and persist through challenges.

**Judge analysis:**

- **MODEL WRONG** — _Rule 3: Observable over evaluative — teacher judgment paired with a concrete action should yield only the action signal_: Model extracts 'showing confidence in his ability' as a separate emotional_indicator signal with self_awareness; golden does not extract this as a separate signal at all.
  - _why:_ Rule 3 (Observable over evaluative): 'showing confidence' is the teacher's interpretive judgment paired with the concrete action of tying the knot — the rubric says to extract the action and drop the evaluative phrase unless it reports the student's own expressed feeling. The golden annotation correctly omits it as a standalone signal.
- **AMBIGUOUS** — _SEL Competencies: self_management — self-discipline, self-motivation sub-skills_: For the knot-tying signal, model assigns no SEL competencies while golden assigns self_management.
  - _why:_ The golden annotation appears to credit self_management for completing the task independently ('on his own'), which could reflect self-discipline or self-motivation. The model's reasoning that independent task completion doesn't inherently demonstrate self_management is defensible, but the rubric's self_management definition includes self-discipline and self-motivation, making golden's assignment reasonable for independent, successful task execution.
- **MODEL WRONG** — _Rule 2: One signal per evidence unit — split when merging hides a distinct second signal of a different type_: Model merges the frustrated/upset emotional reaction and the walking-away/verbal statement into one behavioral_evidence signal; golden splits them into an emotional_indicator (frustrated and upset) and a separate behavioral_evidence (walked away and said he didn't know).
  - _why:_ Rule 2 boundary ambiguity — the emotional reaction and the behavioral response are causally linked but represent distinct signal types (emotional_indicator vs. behavioral_evidence). The rubric's tie-breaker says to split when merging hides a distinct second signal; here the emotional state and the behavioral action are genuinely different types, supporting the golden split. The model's merge also misclassifies the emotional content as behavioral_evidence.
- **MODEL WRONG** — _SEL Competencies: self_awareness — accurate self-perception and identifying emotions; distressed inability statements are not the same as reflective self-assessment_: Model assigns self_awareness to the merged frustration/walking-away signal; golden assigns no SEL competencies to either the emotional_indicator or the behavioral_evidence split signals.
  - _why:_ The model credits self_awareness for the student verbalizing his limitation ('said he didn't know how to complete the knot'), but the rubric maps competencies to demonstrated skills, not to distressed acknowledgments of inability. The golden annotation correctly withholds self_awareness here because saying 'I don't know how' under frustration is not a reflective self-assessment.
- **AMBIGUOUS** — _Rule 2: split vs. merge; concern_flag threshold (Rule 10e); What NOT to Extract: teacher reflections vs. observed behavior_: Model classifies 'George had a hard time coming back to try again, even with help' plus the teacher's framing sentence as a single concern_flag at high confidence; golden splits these into two separate behavioral_evidence signals — one at medium confidence and one at low confidence — and does not classify either as concern_flag.
  - _why:_ The golden annotation treats the teacher's framing sentence ('he is still developing his ability to manage frustration') as a capability/opinion statement (low confidence, behavioral_evidence) rather than pattern evidence elevating the prior sentence to a concern_flag. The rubric's concern_flag threshold requires language indicating a pattern or risk needing attention — 'had a hard time coming back to try again, even with help' combined with 'still developing his ability to manage frustration' does appear to meet that threshold. However, the teacher's framing sentence is arguably a teacher judgment/reflection rather than observed behavior, which the 'What NOT to Extract' section warns against. The golden split and type assignment is defensible under Rule 3 and the capability rule (Rule 9), but the model's concern_flag reading is also defensible given the explicit pattern language.
- **MODEL WRONG** — _SEL Competencies: map to demonstrated skills, not deficits or absent skills_: Model assigns self_management to the concern_flag signal; golden assigns no SEL competencies to either of the two split signals covering the same evidence.
  - _why:_ The golden annotation withholds SEL competencies because the evidence describes a deficit (inability to manage frustration) rather than a demonstrated skill. The rubric maps competencies to skills the student demonstrated, not skills they failed to show. The model's assignment of self_management is inconsistent with this principle.

**Predicted output (4 signals):**

```json
[
  {
    "evidence": "George did a great job tying the \"coada vacii\" knot on his own",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes a specific, observable action — George successfully tying a particular knot independently. Not emotional_indicator because no emotion is described in this segment (confidence is mentioned in the next clause and is the teacher's interpretation). Competencies: none, because tying a knot is a practical/motor skill demonstration without an inherent SEL dimension. One might consider self_management (independent task completion), but completing an assigned task independently does not by itself demonstrate goal-setting, impulse control, or emotional regulation. Confidence: high because the teacher specifies the exact knot ('coada vacii'), confirms it was done independently ('on his own'), and directly observed the action — this is concrete and unambiguous."
  },
  {
    "evidence": "showing confidence in his ability",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: emotional_indicator because 'showing confidence' describes an observed disposition/affect — the teacher perceived the student's emotional state as confident. Not behavioral_evidence because this is about the student's demeanor, not a specific action. Competencies: self_awareness because confidence in one's ability reflects self-efficacy and recognition of one's own strengths. Confidence: medium because 'showing confidence' is the teacher's interpretation of the student's demeanor — the teacher does not describe the specific observable behaviors (body language, verbal statements) that led to this assessment, so there is some interpretive judgment involved."
  },
  {
    "evidence": "When it came to the sliding knot, he initially became frustrated and upset when he realized he couldn't do it by himself. He walked away and said he didn't know how to complete the knot",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes specific observable actions — becoming frustrated, walking away, and verbally stating he didn't know how to complete the knot. These are concrete witnessed behaviors. Not concern_flag on its own because a single instance of frustration with a difficult task is a normal learning challenge; the concern emerges from the broader pattern described later. Competencies: self_awareness because the student recognized and verbalized his limitation ('said he didn't know how to complete the knot'), demonstrating awareness of his own skill boundary. Not self_management because the student did not successfully regulate his frustration — he walked away rather than managing it. Confidence: high because the teacher describes multiple specific, directly observed actions ('became frustrated and upset', 'walked away', 'said he didn't know how to complete the knot') with concrete detail about the trigger ('realized he couldn't do it by himself'). Signal boundary: these two sentences are merged because they describe a single escalation sequence — the emotional reaction (frustrated/upset) leads directly to the behavioral response (walking away and verbal statement). Splitting them would lose the causal chain connecting the trigger to the response."
  },
  {
    "evidence": "George had a hard time coming back to try again, even with help. This is an important learning moment for George, as he is still developing his ability to manage frustration and persist through challenges.",
    "type": "concern_flag",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: concern_flag because the teacher explicitly frames this as a developmental area requiring attention — 'had a hard time coming back to try again, even with help' indicates the student could not recover from frustration even with adult support, and 'still developing his ability to manage frustration and persist through challenges' confirms this is an ongoing pattern, not a one-off struggle. Competencies: self_management because the teacher explicitly identifies frustration management and persistence as the skills George is still developing — these map directly to stress management, impulse control, and self-motivation within self_management. Confidence: high because the teacher provides specific behavioral evidence ('had a hard time coming back to try again, even with help') and explicitly names the developmental concern ('manage frustration and persist through challenges'), leaving no ambiguity about the nature of the concern. Signal boundary: these two sentences are merged because the first describes the specific behavioral difficulty and the second provides the teacher's framing of it as an ongoing developmental pattern — together they form a single concern unit; splitting would separate the evidence from the pattern identification that elevates it to a concern. Concern threshold: 'had a hard time coming back to try again, even with help' indicates that adult intervention was insufficient to re-engage the student, and 'still developing his ability to manage frustration' frames this as an ongoing developmental challenge rather than a momentary setback — the combination of resistance to support and the teacher's explicit identification of a persistent pattern crosses from routine struggle into flaggable concern."
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

### Example 2: `904107b72e5b`

_The model and golden largely agree on signal types and confidence levels, but diverge meaningfully on SEL competency assignments — the model over-infers competencies (self_awareness on story topic choice, self_management/self_awareness on voluntary reading) while the golden over-assigns competencies on the emotional indicator (social_awareness and responsible_decision_making for a simple pride statement). The golden annotation for signal 6 warrants human review, as the added competencies are not grounded in the text._

**Observation** (student_count=1):

> In today's creative writing workshop, Amara chose to write a story about a girl who overcomes her fear of public speaking. She spent extra time planning her story structure before writing. Her narrative included vivid descriptions and dialogue that showed character development. She voluntarily read her story aloud to the class, which is something she has never done before. After reading, she accepted feedback from her peers gracefully and even thanked a classmate who pointed out a spelling error. She told me she felt proud of herself for reading out loud.

**Judge analysis:**

- **MODEL WRONG** — _Rule 4: No inference beyond text_: Model assigns self_awareness to signal 1 ('Amara chose to write a story about a girl who overcomes her fear of public speaking'); golden assigns no SEL competencies.
  - _why:_ The model infers a connection between the story topic and Amara's personal experience with public speaking, but Rule 4 prohibits inferring beyond the text — the observation does not state Amara chose this topic because of her own fear, making the competency assignment speculative.
- **AMBIGUOUS** — _Observation Confidence: medium vs. high threshold_: Model rates signal 3 ('Her narrative included vivid descriptions and dialogue that showed character development') as medium confidence; golden rates it high.
  - _why:_ The model treats 'vivid descriptions' and 'showed character development' as evaluative teacher judgments warranting medium confidence, but the golden treats the specific craft elements named (vivid descriptions, dialogue, character development) as sufficiently concrete to warrant high confidence. The rubric's medium threshold ('broad, missing key context, or mixing observation with opinion') is borderline here.
- **MODEL WRONG** — _Rule 4: No inference beyond text; SEL competencies mapped to demonstrated skills_: Model assigns self_management and self_awareness to signal 4 ('She voluntarily read her story aloud to the class, which is something she has never done before'); golden assigns no SEL competencies.
  - _why:_ The model infers self_management (overcoming internal resistance) and self_awareness (recognizing a personal challenge) from the voluntary action and historical context, but the rubric requires mapping competencies to what is explicitly demonstrated, not inferred. The text does not state Amara regulated emotions or reflected on her limitations — only that she acted voluntarily.
- **AMBIGUOUS** — _SEL Competencies: self_management (impulse control), self_awareness (accurate self-perception), social_awareness (perspective-taking)_: Model assigns relationship_skills and self_management to signal 5 (feedback acceptance); golden assigns self_awareness, social_awareness, and relationship_skills — omitting self_management and adding self_awareness and social_awareness.
  - _why:_ The model focuses on emotional regulation (self_management) for graceful feedback acceptance, while golden emphasizes self_awareness (recognizing one's own reaction to criticism) and social_awareness (understanding the peer's perspective/intent). The rubric supports multiple readings here; 'gracefully' could indicate self_management or self_awareness.
- **GOLDEN WRONG** — _Rule 4: No inference beyond text; SEL competencies mapped to what is explicitly demonstrated_: Model assigns only self_awareness to signal 6 ('She told me she felt proud of herself for reading out loud'); golden assigns self_awareness, social_awareness, and responsible_decision_making.
  - _why:_ Golden adds social_awareness and responsible_decision_making, but the evidence is a simple self-reported emotion ('felt proud of herself for reading out loud') with no explicit reference to others' perspectives (social_awareness) or decision evaluation (responsible_decision_making). These additional competencies appear to be inferred rather than evidenced.
- **MODEL WRONG** — _Rule 1: Evidence must be verbatim quote from observation_: Model's evidence for signal 5 omits 'After reading,' prefix present in golden ('After reading, she accepted feedback...' vs. 'she accepted feedback...').
  - _why:_ Minor evidence boundary difference — the model dropped the temporal phrase 'After reading,' which golden includes. This is a minor omission but 'After reading' provides sequencing context.

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
    "reasoning": "Type: behavioral_evidence because the teacher describes a specific, observable creative choice Amara made — selecting a particular story topic. Competencies: self_awareness because the chosen theme (overcoming fear of public speaking) directly mirrors what Amara herself later does (reading aloud for the first time), suggesting she is reflecting on her own experiences and emotions through her writing. Confidence: high because the teacher directly observed the specific topic Amara chose, leaving no ambiguity."
  },
  {
    "evidence": "She spent extra time planning her story structure before writing",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher observed a specific action — Amara deliberately spending additional time on planning before writing. Competencies: self_management because taking extra time to plan before executing demonstrates organizational skills, self-discipline, and goal-directed behavior. Confidence: high because the teacher directly observed the behavior and specifies what she did ('planning her story structure') and when ('before writing'), making this concrete and unambiguous."
  },
  {
    "evidence": "Her narrative included vivid descriptions and dialogue that showed character development",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because the teacher describes observable qualities of Amara's written work — vivid descriptions, dialogue, and character development. Competencies: none, because these are academic writing skills rather than demonstrations of SEL competencies. One might consider social_awareness (perspective-taking through character development), but the evidence describes a writing technique, not the student demonstrating empathy or understanding of others' perspectives in a social context. Confidence: medium because 'vivid descriptions' and 'showed character development' are the teacher's evaluative assessments of the writing quality — the teacher read the work but does not provide specific examples or quotes from the narrative."
  },
  {
    "evidence": "She voluntarily read her story aloud to the class, which is something she has never done before",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management",
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher directly witnessed a specific, observable action — Amara reading aloud to the class voluntarily. Competencies: self_management because voluntarily doing something she has never done before demonstrates self-motivation and overcoming internal resistance or anxiety; self_awareness because the teacher's note that 'she has never done before' implies Amara recognized this was a challenge for her and chose to push past it, reflecting awareness of her own limitations and growth. Confidence: high because the teacher directly observed the action ('read her story aloud to the class'), specifies it was voluntary, and provides concrete historical context ('never done before'), making this highly specific and unambiguous."
  },
  {
    "evidence": "she accepted feedback from her peers gracefully and even thanked a classmate who pointed out a spelling error",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes specific, observable actions — accepting feedback and thanking a classmate. Competencies: relationship_skills because accepting peer feedback and thanking a classmate demonstrates healthy communication, social engagement, and cooperation; self_management because receiving criticism gracefully requires emotional regulation and impulse control. Confidence: high because the teacher describes two concrete, specific actions (accepting feedback, thanking a specific classmate for a specific correction) that were directly witnessed. Signal boundary: these two actions are merged because they describe a single feedback interaction — the acceptance and the thanking are part of the same social exchange, and splitting them would lose the context that the thanking was in response to critical feedback, which is what makes it meaningful."
  },
  {
    "evidence": "She told me she felt proud of herself for reading out loud",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: emotional_indicator because the student directly communicated her emotional state — feeling proud — to the teacher. Not behavioral_evidence because the core content is about how the student felt, not what she did. Competencies: self_awareness because Amara is recognizing, naming, and articulating her own emotion (pride) and connecting it to a specific accomplishment (reading out loud), demonstrating the ability to identify her own feelings and assess her strengths. Confidence: high because these are the student's own reported words conveyed through direct dialogue ('She told me she felt proud'), giving the teacher first-hand access to the student's emotional experience with no inference required."
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

### Example 3: `5a0230aae3d8`

_The model and golden largely agree on evidence boundaries and signal types for most signals, but the model makes three meaningful classification errors: attributing self_management to a vague focus observation, omitting relationship_skills from the participation signal, and misclassifying students' verbal feedback as an emotional_indicator rather than behavioral_evidence. The golden annotation also differs on confidence for the game-name context_marker and omits the 'Crew Meet' standalone signal, both of which are defensible either way. The three competency/type errors warrant attention as they reflect systematic over-inference from evaluative language._

**Observation** (student_count=15):

> Crew Meet was a great opportunity to practice focus skills with the Upper Primary crew. We played a game called ""Hocus Pocus, Everybody Focus."" From my perspective, the children were more focused than last week. All members of the crew participated, and at the end they told me that the game was both playful and useful. Together, we acknowledged that focus is an important skill that helps us beyond school.

**Judge analysis:**

- **AMBIGUOUS** — _Rule 7: A short observation may yield one signal; don't pad_: Model extracts 'Crew Meet' as a standalone context_marker signal; golden does not include this signal at all.
  - _why:_ The golden annotator likely treated 'Crew Meet' as redundant with the game-name context_marker already extracted, or considered it too minimal to warrant its own signal. The rubric does not prohibit extracting it, but Rule 2 and the 'no padding' guidance (Rule 7) could support omitting it as non-additive.
- **AMBIGUOUS** — _Observation Confidence: high — evidence directly states the behavior/context with minimal judgment_: Model assigns 'high' confidence to the game-name context_marker; golden assigns 'medium'.
  - _why:_ Golden likely capped confidence at medium because the observation is a group observation with 15 unnamed students (Rule 8), or because the game name alone provides limited actionable detail. However, for a context_marker, confidence reflects how specific and observable the evidence is — the game name is explicitly stated, which typically warrants high confidence.
- **MODEL WRONG** — _SEL Competencies: map to demonstrated skills; Rule 3: Observable over evaluative_: Model assigns self_management to 'the children were more focused than last week'; golden assigns no SEL competencies to this signal.
  - _why:_ Golden likely reasoned that a vague group-level comparative statement ('more focused') does not demonstrate a specific SEL skill — the behavior is too unspecified to attribute self_management. The rubric maps competencies to demonstrated skills, and 'more focused' is an observer's judgment rather than a witnessed self-regulation action.
- **MODEL WRONG** — _SEL Competencies: relationship_skills — cooperation, teamwork, social engagement_: Model assigns no SEL competencies to 'All members of the crew participated'; golden assigns relationship_skills.
  - _why:_ Golden reasoned that full group participation in a crew activity demonstrates cooperation and teamwork (relationship_skills sub-skills). The model argued participation was too vague to attribute any competency, but the rubric supports mapping relationship_skills when group cooperation is the evident behavior.
- **MODEL WRONG** — _Signal Types: emotional_indicator — affect or emotional state visible in text; behavioral_evidence — specific actions, strategies, choices; Observation Confidence: high — directly states behavior_: Model classifies 'at the end they told me that the game was both playful and useful' as emotional_indicator with self_awareness and medium confidence; golden classifies it as behavioral_evidence with no SEL competencies and high confidence.
  - _why:_ The model interpreted 'playful and useful' as expressing feelings/affect, but the rubric's emotional_indicator requires observed or expressed emotions — 'playful and useful' is an evaluative opinion about the game, not an emotional state. Golden correctly classifies it as behavioral_evidence (students verbally communicated feedback). Golden assigns high confidence because the teacher directly quotes what students said. The model's self_awareness attribution is also unsupported — articulating an opinion about an activity is not the same as recognizing one's own emotions or strengths.

**Predicted output (5 signals):**

```json
[
  {
    "evidence": "Crew Meet",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: context_marker because 'Crew Meet' identifies the specific setting/event framing the observation — it describes the situation, not a student action or emotion. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: high because the teacher explicitly names the event."
  },
  {
    "evidence": "We played a game called \"Hocus Pocus, Everybody Focus.\"",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: context_marker because this identifies the specific activity used during the session — it frames what was happening, not what any individual student did. Competencies: none, because naming an activity does not demonstrate any SEL skill. Confidence: high because the teacher explicitly names the game."
  },
  {
    "evidence": "the children were more focused than last week",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "low",
    "reasoning": "Type: behavioral_evidence because 'more focused' describes an observable behavioral quality the teacher perceived in the group. Not emotional_indicator because focus is a behavioral state, not an emotion. Competencies: self_management because maintaining focus during an activity reflects self-discipline and attention regulation. Confidence: low because this is a vague, comparative group-level judgment ('more focused than last week') with no specific observable actions described, and the teacher qualifies it with 'From my perspective,' acknowledging subjectivity. Additionally, with 15 students and no named individuals, the observation cannot be attributed to any specific student."
  },
  {
    "evidence": "All members of the crew participated",
    "type": "behavioral_evidence",
    "sel_competencies": [],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because participation is an observable action the teacher witnessed across the group. Not concern_flag because full participation is positive. Competencies: none, because 'participated' is too vague to determine which SEL competency was demonstrated — participation could reflect self_management (engagement), relationship_skills (cooperation), or none at all depending on what the participation looked like, which is not described. Confidence: medium because the teacher clearly states everyone participated, which is a definite claim, but 'participated' is broad and unspecified — no details about what participation looked like — and it describes a group of 15 unnamed students rather than an individual."
  },
  {
    "evidence": "at the end they told me that the game was both playful and useful",
    "type": "emotional_indicator",
    "sel_competencies": [
      "self_awareness"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: emotional_indicator because the students expressed their feelings and assessment of the experience directly to the teacher — 'playful and useful' conveys positive affect and reflective evaluation of the activity. Not behavioral_evidence because the core content is the students' expressed feelings/opinions, not an action. Competencies: self_awareness because the students reflected on their own experience and articulated what they found valuable, demonstrating the ability to recognize and communicate their own perceptions. Confidence: medium because the teacher reports what the group said, providing some direct evidence, but it is a collective statement from 15 unnamed students with no individual attribution, and the exact words may be paraphrased."
  }
]
```

**Golden output (4 signals):**

```text
"signals": [
    {
      "evidence": "We played a game called ""Hocus Pocus, Everybody Focus."" ",
      "type": "context_marker",
      "sel_competencies": [],
      "observation_confidence": "medium"
    },
    {
      "evidence": "the children were more focused than last week",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "low"
    },
    {
      "evidence": "All members of the crew participated",
      "type": "behavioral_evidence",
      "sel_competencies": ["relationship_skills"],
      "observation_confidence": "medium"
    },
    {
      "evidence": "they told me that the game was both playful and useful",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    }
  ]
```

### Example 4: `98f965078775`

_The model and golden broadly agree on signal type (behavioral_evidence) and core competency (relationship_skills) across the observation, but diverge on three issues: the model merges two distinct behavioral clauses that the rubric's Rule 2 supports splitting, the model applies Rule 8's medium-confidence cap to unnamed group actors where the golden does not, and there are competency mapping differences on the conflict-resolution signal. The merge/split disagreement is the clearest rubric-supported difference and warrants a human review of the golden annotation to confirm the split and the confidence levels assigned._

**Observation** (student_count=6):

> The crew worked together on a mural project. They discussed color choices democratically and took turns painting different sections. When one member accidentally smudged another's section, they resolved it calmly by offering to help fix it.

**Judge analysis:**

- **AMBIGUOUS** — _Signal Types: context_marker — setting, conditions, or social configuration that frames the observation_: The model extracts 'The crew worked together on a mural project.' as a context_marker signal; the golden annotation does not include this signal at all.
  - _why:_ The rubric supports extracting context markers that frame the observation (Rule 1, context_marker definition), so the model's extraction is defensible. The golden may have omitted it as implicit background, but the rubric does not exclude it.
- **MODEL WRONG** — _Rule 2: One signal per evidence unit — 'a sentence describing multiple distinct skills, subjects, or moments is multiple units — split it'_: The model merges 'They discussed color choices democratically and took turns painting different sections' into one signal; the golden splits them into two separate signals.
  - _why:_ Rule 2 states that a sentence describing multiple distinct skills or moments should be split. The golden treats democratic discussion and turn-taking as two distinct behavioral units. The model's reasoning argues they are complementary aspects of the same cooperative dynamic, but the rubric's tie-breaker favors splitting when merging hides a distinct second signal — and these are separable actions.
- **AMBIGUOUS** — _Rule 8: Group observations with unnamed actors — confidence capped at medium; but high confidence requires specific observable actions grounded in what was directly seen_: The model assigns 'medium' confidence to 'took turns painting different sections' (merged), while the golden assigns 'high' confidence to this clause as a standalone signal.
  - _why:_ The model applies Rule 8 (unnamed group actors capped at medium) to the merged signal. However, 'took turns painting different sections' describes a concrete, directly observable group action with no inference required — Rule 8's cap applies when attribution is uncertain, but the action itself is unambiguous. The golden's 'high' confidence reflects the specificity of the observable action rather than individual attribution.
- **AMBIGUOUS** — _Rule 8: Group observations with unnamed actors — confidence capped at medium_: The model assigns 'medium' confidence to the smudge/resolution signal citing Rule 8 (unnamed actors); the golden assigns 'high' confidence to the same evidence.
  - _why:_ The golden appears not to apply Rule 8's cap here, treating the concrete sequence of events (smudge → calm resolution → offer to help) as sufficient for high confidence. The model's Rule 8 application is textually justified ('one member', 'they'), but the golden prioritizes the specificity of the described action over the attribution ambiguity.
- **AMBIGUOUS** — _SEL Competencies: social_awareness (empathy, perspective-taking); responsible_decision_making (solving problems, constructive choices); self_management (impulse control, emotional regulation)_: The model maps the smudge/resolution signal to 'self_management' and 'relationship_skills'; the golden maps it to 'relationship_skills', 'social_awareness', and 'responsible_decision_making' — omitting self_management and adding social_awareness and responsible_decision_making.
  - _why:_ The golden includes social_awareness (offering to help fix reflects empathy/perspective-taking toward the affected peer) and responsible_decision_making (choosing a constructive resolution). The model excluded social_awareness arguing the evidence shows action not perspective-taking, and included self_management for the calm response. The rubric supports social_awareness when a student takes another's perspective in a conflict, and responsible_decision_making for constructive conflict resolution choices — both are defensible. Self_management for 'calmly' is also defensible but the golden omits it.
- **AMBIGUOUS** — _SEL Competencies: responsible_decision_making — constructive choices about personal behavior and social interactions; relationship_skills — communicate clearly, cooperate with others_: The model includes 'responsible_decision_making' for the democratic color-choice signal; the golden omits it, mapping only to 'relationship_skills'.
  - _why:_ The model argues democratic decision-making reflects evaluating options and making collective decisions (responsible_decision_making). The golden treats this purely as a relationship/cooperation behavior. The rubric's responsible_decision_making definition includes 'analyzing situations' and 'solving problems,' which could apply, but democratic discussion in a group context is primarily a relationship_skills behavior — the golden's narrower mapping is defensible.

**Predicted output (3 signals):**

```json
[
  {
    "evidence": "The crew worked together on a mural project.",
    "type": "context_marker",
    "sel_competencies": [],
    "observation_confidence": "high",
    "reasoning": "Type: context_marker because this sentence establishes the setting and activity (a mural project) that frames the rest of the observation — it describes the situation, not a specific student action or emotion. Competencies: none, because context markers describe circumstances, not student-demonstrated skills. Confidence: high because the teacher explicitly and unambiguously names the specific activity and group configuration."
  },
  {
    "evidence": "They discussed color choices democratically and took turns painting different sections.",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "responsible_decision_making"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because 'discussed color choices democratically' and 'took turns painting different sections' describe observable group actions — collaborative discussion and turn-taking. Not emotional_indicator because no feelings are described. Competencies: relationship_skills because democratic discussion and turn-taking demonstrate cooperation, communication, and teamwork; responsible_decision_making because making color choices democratically reflects a group process of evaluating options and making constructive collective decisions. Confidence: medium because this is a group observation with student_count of 6 and no individual actors are named — the actions are attributed to 'they' collectively, so we cannot confirm which specific students demonstrated these behaviors. Per Rule 8, confidence is capped at medium for unnamed group actors. Signal boundary: the two clauses are merged because they describe the same collaborative dynamic during the same activity — discussing choices and taking turns are complementary aspects of the group's cooperative process, not two distinct behavioral events."
  },
  {
    "evidence": "When one member accidentally smudged another's section, they resolved it calmly by offering to help fix it.",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "self_management"
    ],
    "observation_confidence": "medium",
    "reasoning": "Type: behavioral_evidence because 'resolved it calmly by offering to help fix it' describes a specific observable action — a conflict resolution behavior the teacher witnessed. Not emotional_indicator because 'calmly' describes the manner of the action rather than a reported or expressed emotional state. Competencies: relationship_skills because resolving a peer conflict constructively and offering to help fix the mistake demonstrates conflict negotiation and cooperation; self_management because responding calmly to an accidental smudge (rather than reacting with frustration or anger) demonstrates emotional regulation and impulse control. Not social_awareness because while empathy may underlie the offer to help, the evidence describes the action of helping, not perspective-taking or empathizing. Confidence: medium because the actors are unnamed ('one member', 'they') — per Rule 8, confidence is capped at medium since the specific students involved cannot be identified. The teacher does describe a concrete sequence of events (smudge → calm resolution → offer to help), which would otherwise support high confidence."
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

### Example 5: `e2ec6d89548b`

_The model and golden largely agree on evidence boundaries, types, and confidence levels, but diverge on three meaningful issues: (1) the model incorrectly merges the emotional frustration and behavioral dismissal into one signal rather than splitting them into an emotional_indicator and a behavioral_evidence; (2) the model maps social_awareness as a deficit rather than a demonstrated skill; and (3) the model omits responsible_decision_making from the acknowledgment signal. These differences warrant a review of the golden annotation only for the self_management/relationship_skills split on signal 1, which is genuinely ambiguous._

**Observation** (student_count=1):

> Oscar showed great initiative by volunteering to be the group leader for the history project. He organized the research materials and assigned roles to each team member. However, he became frustrated when his teammates suggested changes to his plan and dismissed their ideas without listening. By the end of the session, he acknowledged that he should have been more open to others' suggestions.

**Judge analysis:**

- **AMBIGUOUS** — _Rule 3: Observable over evaluative; SEL competency mapping requires demonstrated skill_: Model includes 'self_management' for signal 0 (volunteering to be group leader), while golden assigns no SEL competencies to this signal.
  - _why:_ Rubric Rule 3 instructs extracting the action over the evaluative phrase 'showed great initiative'; the act of volunteering alone is a proactive choice but does not clearly demonstrate a self_management sub-skill (impulse control, stress management, goal-setting, etc.) in a witnessed, specific way — golden treats it as a plain behavioral observation without a demonstrated SEL competency.
- **AMBIGUOUS** — _SEL Competencies: relationship_skills sub-skills include teamwork; self_management sub-skills include organizational skills_: Model includes 'relationship_skills' for signal 1 (organized materials and assigned roles), while golden assigns only 'self_management'.
  - _why:_ Assigning roles to team members could be seen as relationship_skills (teamwork/coordination) or simply as a leadership/organizational task under self_management. Golden appears to treat role assignment as part of organizational self_management rather than an interpersonal relationship_skills demonstration, since the evidence doesn't describe how Oscar interacted with teammates but only that he assigned roles.
- **MODEL WRONG** — _Rule 2: One signal per evidence unit — if merging hides a distinct second signal, split; Signal Types: emotional_indicator vs. behavioral_evidence_: Model merges 'became frustrated' and 'dismissed their ideas without listening' into one behavioral_evidence signal; golden splits them into two signals — an emotional_indicator ('became frustrated') and a behavioral_evidence ('dismissed their ideas without listening').
  - _why:_ The rubric's Rule 2 tie-breaker states: 'if merging hides a distinct second signal, split.' Here, the frustration is a distinct emotional state and the dismissal is a distinct behavioral action — they are different signal types (emotional_indicator vs. behavioral_evidence), so splitting is clearly supported. The model's reasoning acknowledges the emotional component but incorrectly subsumes it.
- **MODEL WRONG** — _SEL Competencies: map to demonstrated skills, not deficits_: Model assigns 'social_awareness' to the merged frustration/dismissal signal; golden assigns no SEL competencies to either the emotional_indicator or the behavioral_evidence split signals.
  - _why:_ The rubric maps competencies to skills the student demonstrated, not skills they failed to show. Dismissing ideas without listening reflects an absence of social_awareness, not a demonstration of it. Golden correctly assigns no competencies to these signals.
- **MODEL WRONG** — _SEL Competencies: responsible_decision_making — reflecting, evaluating consequences of actions_: Model assigns 'self_awareness' and 'social_awareness' to the acknowledgment signal; golden assigns 'self_awareness', 'social_awareness', AND 'responsible_decision_making'.
  - _why:_ The acknowledgment ('should have been more open to others' suggestions') involves reflecting on one's behavior and its impact on others — this maps to responsible_decision_making's sub-skills of reflecting and evaluating consequences of actions. The model omitted this competency.

**Predicted output (4 signals):**

```json
[
  {
    "evidence": "Oscar showed great initiative by volunteering to be the group leader for the history project.",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because 'volunteering to be the group leader' is a specific, observable action the teacher witnessed. The evaluative phrase 'showed great initiative' is paired with the concrete action, so per Rule 3 we extract the action. Competencies: self_management because volunteering for a leadership role demonstrates self-motivation and proactive goal-directed behavior. Not relationship_skills because the act of volunteering is an individual decision, not an interpersonal interaction. Confidence: high because the teacher describes a specific, unambiguous action — Oscar volunteered for a defined role in a specific project."
  },
  {
    "evidence": "He organized the research materials and assigned roles to each team member.",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "relationship_skills",
      "self_management"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because the teacher describes two specific, observable actions — organizing materials and assigning roles. Competencies: relationship_skills because assigning roles to team members is a direct demonstration of teamwork and coordination with peers; self_management because organizing research materials demonstrates organizational skills and self-discipline in structuring work. Confidence: high because both actions are concrete and specific — the teacher directly observed what Oscar did with no ambiguity or interpretation."
  },
  {
    "evidence": "he became frustrated when his teammates suggested changes to his plan and dismissed their ideas without listening",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "social_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because 'dismissed their ideas without listening' is a specific, observable action the teacher witnessed. While 'became frustrated' includes an emotional component, the core of this evidence unit is the behavioral response to the frustration — dismissing ideas. Not concern_flag because this is a single instance of difficulty accepting feedback, not described as a recurring pattern. Competencies: social_awareness because dismissing teammates' ideas without listening represents a failure to take others' perspectives — the competency is relevant because the student's behavior directly relates to (a lack of) perspective-taking and respect for others' input. Confidence: high because the teacher describes a specific trigger ('teammates suggested changes'), a specific emotional response ('became frustrated'), and a specific behavioral outcome ('dismissed their ideas without listening') — all directly observed with no ambiguity. Signal boundary: the frustration and the dismissal are merged because the frustration is the cause and the dismissal is the immediate behavioral consequence — they form a single escalation unit; splitting would lose the causal connection."
  },
  {
    "evidence": "By the end of the session, he acknowledged that he should have been more open to others' suggestions.",
    "type": "behavioral_evidence",
    "sel_competencies": [
      "self_awareness",
      "social_awareness"
    ],
    "observation_confidence": "high",
    "reasoning": "Type: behavioral_evidence because 'acknowledged' is a specific verbal action the teacher witnessed — the student made a reflective statement. Not emotional_indicator because the content is a reflective acknowledgment about behavior, not an expression of an emotional state. Competencies: self_awareness because acknowledging a personal shortcoming ('should have been more open') demonstrates accurate self-perception and recognition of one's own limitations; social_awareness because the acknowledgment specifically concerns openness to others' perspectives, showing the student recognized the value of his teammates' input and their right to contribute. Confidence: high because the teacher reports a specific moment ('by the end of the session') and a specific verbal acknowledgment with clear content, leaving no ambiguity about what was said or when."
  }
]
```

**Golden output (5 signals):**

```text
"signals": [
    {
      "evidence": "volunteering to be the group leader for the history project",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "He organized the research materials and assigned roles to each team member",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_management"],
      "observation_confidence": "high"
    },
    {
      "evidence": "he became frustrated when his teammates suggested changes to his plan",
      "type": "emotional_indicator",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "dismissed their ideas without listening",
      "type": "behavioral_evidence",
      "sel_competencies": [],
      "observation_confidence": "high"
    },
    {
      "evidence": "By the end of the session, he acknowledged that he should have been more open to others' suggestions",
      "type": "behavioral_evidence",
      "sel_competencies": ["self_awareness", "social_awareness", "responsible_decision_making"],
      "observation_confidence": "high"
    }
  ]
```

_...and 33 more observations with differences._
