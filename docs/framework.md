# Analysis Framework

How to extract per-student insights from SEL observations through a layered extraction → contextualization → accumulation → synthesis pipeline.

## The Problem

Teachers write observations in natural language — often mixing languages, varying in specificity, covering multiple SEL competencies in a single comment. The platform already does standard-matching (via Lila), but the raw observation text contains far more signal than a single standard tag captures.

This framework defines how to systematically extract, contextualize, accumulate, and synthesize that signal into actionable student profiles.

## Data Shape

Each observation record contains:

| Field | Description | Example |
|-------|-------------|---------|
| `comment` | Free-text observation (EN/ES) | "Angel has improved his focus in English class and today he raised his hand to answer almost every question" |
| `subject` | Curriculum framework | CASEL, CCB Values, Approaches to Teaching and Learning, Ethics and Values |
| `area` | SEL domain | Self-management, Empathy, Resilience, Collaboration skills |
| `standard` | Matched learning standard | "Manages his/her emotions, thoughts, and behaviors effectively..." |
| `mastery` | Performance level | Low/Bajo, High/Alto, Superior/Superior |
| `score` | Numeric mastery (1-4) | 3 |
| `reason_for_tag` | AI explanation of the standard match | "Students recognized a peer's emotional state and acted with compassion" |
| `student_id` | Target student | UUID |
| `crew` | Grade/cohort | Year 6, Year 7, Year 11 |

Key observations from the preview dataset:
- **Bilingual**: Comments appear in both English and Spanish — extraction must be language-agnostic
- **Multi-tagged**: A single comment can map to multiple frameworks (e.g., same empathy observation tagged to both CCB Values and CASEL)
- **Group observations**: Same `comment_key` appears for multiple students — the teacher described a group moment, not an individual. `student_names` field lists all students covered.
- **Group size guardrail**: Observations with 6+ students are definitively group content — signals apply uniformly and skip per-student attribution in Layer 1.5/2. Only groups of 2-5 students may contain individually differentiable signals.
- **Varying specificity**: Ranges from "This group collaborated effectively" (vague) to "raised his hand to answer almost every question I asked about elements of speeches" (concrete)

---

## Layer 1: Raw Extraction

**Goal**: Take one observation text and extract structured insight signals — with zero knowledge of the student.

### What gets extracted

| Signal | Description | Example from dataset |
|--------|-------------|---------------------|
| **SEL competencies demonstrated** | Which CASEL domains are visible in the text | Self-management, Social awareness |
| **Behavioral evidence** | Concrete, observable actions the teacher described | "raised his hand to answer almost every question", "pidieron permiso para ir a hablar con él" |
| **Emotional indicators** | Affect or emotional state signals | "positive attitude and open mindedness", "se puso triste" |
| **Context markers** | Setting, conditions, triggers | "unsupervised", "on a trip abroad for a month", "al iniciar la clase" |
| **Mastery signals** | Indicators of skill level (emerging, developing, proficient, exceeding) | Proactive behavior without prompting → exceeding; learning by repetition → emerging |
| **Concern flags** | Language that suggests risk or regression | "hace uso frecuente de palabras soeces" |
| **Observation type** | Individual vs. group | Group (shared `comment_key`) vs. individual |

### Extraction rules

1. **Language-agnostic**: The model must handle EN/ES without translation. Extract in the language of the comment; normalize signal names to English.
2. **Evidence-first**: Every extracted signal must point to a specific phrase or sentence in the original comment as its evidence anchor.
3. **No inference beyond text**: Layer 1 does not know who the student is, what they've done before, or what other observations exist. It extracts only what the text says.
4. **Multi-signal**: A single observation can yield multiple signals. "Vieron que un compañero se puso triste... pidieron permiso para ir a hablar con él, calmarlo y escucharlo" yields: social awareness (recognizing peer's state), empathy (choosing to comfort), self-regulation (asking permission first).

### Output schema

```json
{
  "observation_id": "string",
  "language": "es | en",
  "signals": [
    {
      "type": "sel_competency | behavioral_evidence | emotional_indicator | context_marker | mastery_signal | concern_flag",
      "value": "string — the extracted insight",
      "evidence": "string — exact quote from comment",
      "confidence": 0.0-1.0
    }
  ],
  "observation_type": "individual | group",
  "insight_density": "low | medium | high"
}
```

`insight_density` is a meta-signal: how much extractable information does this observation contain? This feeds directly into quality scoring later.

---

## Layer 1.5: Student-Contextualized Extraction

**Goal**: Re-interpret Layer 1 signals through the lens of what we already know about this student.

### Why a separate layer

Layer 1 tells us "this observation shows self-management." Layer 1.5 tells us "this observation shows self-management, and this is significant because this student has historically struggled with self-regulation" or "this is consistent with their established pattern."

The same observation text means different things for different students.

### Inputs

- Layer 1 extraction output
- Student's existing profile (from Layer 2, if available — empty for first observation)
- Student metadata: `crew`, historical `area` distribution, mastery trajectory

### What gets added

| Signal | Description | Example |
|--------|-------------|---------|
| **Novelty** | Is this a new competency for the student, or a known strength? | First empathy observation → high novelty |
| **Trajectory** | Does this confirm, extend, or contradict the student's pattern? | Angel "improved his focus" → upward trajectory on attention |
| **Salience** | How important is this signal given the student's profile? | Concern flag on a student with no prior concerns → high salience |
| **Cross-competency links** | Does this signal connect to other areas in the student's profile? | Empathy + self-regulation in same event → relationship skills emerging |

### Output schema

```json
{
  "observation_id": "string",
  "student_id": "string",
  "contextualized_signals": [
    {
      "base_signal": "reference to Layer 1 signal",
      "novelty": "new | reinforcing | contradicting",
      "trajectory": "emerging | developing | stable | declining",
      "salience": "routine | notable | significant",
      "cross_links": ["array of related competency areas"]
    }
  ],
  "profile_impact": "minimal | moderate | high"
}
```

`profile_impact` indicates how much this observation should shift the student's cumulative profile. A routine reinforcement of a known strength = minimal. A first-ever concern flag = high.

---

## Layer 2: Profile Accumulation

**Goal**: Build and maintain a cumulative student profile from the stream of contextualized observations over time.

### Profile structure

Each student profile is a living document organized by SEL competency area, with temporal snapshots that preserve history.

```json
{
  "student_id": "string",
  "crew": "Year 7",
  "profile_version": "2025-10-28",
  "last_updated": "timestamp",
  "observation_count": 15,
  "competency_map": {
    "self_management": {
      "observation_count": 6,
      "current_level": "proficient",
      "trajectory": "stable",
      "evidence_summary": "Consistently demonstrates self-regulation...",
      "recent_signals": ["reference to latest observations"],
      "snapshots": [
        { "date": "2025-09", "level": "developing", "observation_count": 3 },
        { "date": "2025-10", "level": "proficient", "observation_count": 6 }
      ]
    }
  },
  "strengths": ["self_management", "social_awareness"],
  "growth_areas": ["respect"],
  "flags": []
}
```

### Accumulation rules

1. **Snapshot on change**: Create a new temporal snapshot whenever a competency level shifts or a significant signal arrives.
2. **Weighted recency**: Recent observations carry more weight than older ones when computing `current_level`. A student who struggled in March but improved by October should reflect the October state.
3. **Group observation handling**: When an observation is tagged as group (`observation_type: group`), the signals are attributed to the student but with a `group_context` flag — individual demonstrations carry more weight than group ones.
4. **Multi-framework reconciliation**: The same observation may be tagged to CASEL, CCB Values, and ATL. The profile accumulates under normalized CASEL competency areas, with framework-specific scores preserved as metadata.
5. **Minimum evidence threshold**: A competency level requires at least 3 observations before it's considered "established" rather than "emerging."

---

## Layer 3: Wellness & Risk Detection

**Goal**: Detect temporal patterns across a student's profile that indicate wellness concerns, regression, or emerging risk.

### Pattern types

| Pattern | Detection logic | Example |
|---------|----------------|---------|
| **Regression** | Competency level declining across 2+ snapshots | Self-management: proficient → developing over 2 months |
| **Sudden concern** | First-ever concern flag on a student with clean history | "hace uso frecuente de palabras soeces" on a student with no prior flags |
| **Isolation signal** | Drop in social competencies (empathy, collaboration, social awareness) without corresponding academic decline | Student stops appearing in group observations; individual observations show self-management only |
| **Disengagement** | Observation frequency drops significantly | Student went from 4 observations/month to 0 in 6 weeks |
| **Consistent struggle** | A growth area that hasn't improved despite multiple observations | Respect area stuck at Low across 5+ observations over 3 months |

### Risk levels

| Level | Meaning | Action |
|-------|---------|--------|
| **Monitor** | Pattern worth watching, no action needed yet | Surface to teacher dashboard |
| **Alert** | Pattern suggests intervention may be needed | Notify homeroom teacher / crew leader |
| **Escalate** | Multiple converging risk signals | Flag for counselor / student support team |

### Important constraints

- This layer detects patterns, it does not diagnose. Language must always be observational, never clinical.
- Risk signals are surfaced to educators as prompts for attention, not conclusions.
- Absence of observations is itself a signal (disengagement), but must be cross-referenced with attendance data to avoid false positives (student was absent vs. student was present but unobserved).

---

## Quality Scoring (Derived)

**Goal**: Score observation quality based on how much insight it yields through the pipeline.

### Connection to existing rubric

The annotation rubric (`annotation-rubric.md`) scores observations on 4 dimensions: Specificity, Evidence, Curriculum Alignment, Actionability. Quality scoring in this framework is the **pipeline-derived** version of the same idea:

| Rubric dimension | Framework equivalent |
|-----------------|---------------------|
| Specificity | Number and granularity of behavioral evidence signals in Layer 1 |
| Evidence | Proportion of signals with high-confidence evidence anchors |
| Curriculum Alignment | Whether extracted SEL competencies map cleanly to standards |
| Actionability | `profile_impact` score in Layer 1.5 — does this observation change what we know about the student? |

### Composite quality signal

```
insight_yield = (signal_count × avg_confidence × profile_impact_weight) / observation_length_normalized
```

An observation that is short but produces high-confidence, high-impact signals scores higher than a long observation that yields vague, low-confidence extractions.

### Feedback loop

Quality scores can be fed back to teachers:
- "Your recent observation about Angel's focus had high insight yield — the specific detail about hand-raising behavior helped us update his profile."
- "This observation was tagged to 2 standards but the text was too general for us to extract specific evidence. Adding concrete examples would help."

This closes the loop: better observations → richer extraction → more useful profiles → better teacher feedback → even better observations.