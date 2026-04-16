# Layer 1: Glossary & Evaluation (Quick Reference)

## Output Fields

**Observation-level**
| Field | Values | Set by |
|---|---|---|
| `observation_type` | `individual` / `group` | Code: `student_count == 1 → individual`, else `group` |
| `signal_count` | integer | Code: `len(signals)` |

**Signal-level**
| Field | Values | Notes |
|---|---|---|
| `evidence` | verbatim quote | Must appear in observation text |
| `type` | one of 4 (below) | Mutually exclusive |
| `sel_competencies` | 0+ CASEL labels | Only for **demonstrated** skills |
| `observation_confidence` | `high` / `medium` / `low` | How observable the evidence is |
| `reasoning` | string | Justifies (a) type (b) competencies (c) confidence (d) boundary (e) concern threshold |

---

## Signal Types

| Type | What it is | Test |
|---|---|---|
| `behavioral_evidence` | Observable actions | Can you point to something the student **did**? |
| `emotional_indicator` | Named affect/feelings | Was the emotion stated by teacher or student? |
| `context_marker` | Setting, conditions, timeframe | Does it describe the situation, not the student? |
| `concern_flag` | Pattern/risk needing attention | Does language show **recurrence** ("repeatedly", "can't", "wasn't new")? |

**Concern threshold:**
- **NOT concern:** "needed a bit of help", one-off difficulty
- **IS concern:** "repeatedly refuses", "can't control", "wasn't new", crying + "can't do hard things"

---

## SEL Competencies (CASEL)

| Label | Core idea |
|---|---|
| `self_awareness` | Recognize own emotions, strengths, values |
| `self_management` | Regulate emotions, impulse control, goal setting |
| `social_awareness` | Perspective-taking, empathy |
| `relationship_skills` | Communication, teamwork, conflict resolution |
| `responsible_decision_making` | Constructive choices, ethical reasoning |

**Rule:** Only map when the skill is **demonstrated**. Absence ≠ mapping.

---

## Confidence Levels

| Level | Meaning | Example |
|---|---|---|
| `high` | Concrete action, minimal judgment | "Solved 4 of 5 problems using partial products" |
| `medium` | Implied but not stated | "Worked on fractions and showed understanding" |
| `low` | Vague, generic, judgment-only | "Did well today" / "Has a great attitude" |

**Caps:**
- Unnamed group actor ("one student", "some") → max `medium`
- Capability statements ("can do", "is beginning to") → max `low` unless witnessed

---

## Thresholds

| Threshold | Value | Where | Why |
|---|---|---|---|
| Evidence overlap match | ≥ 0.5 Jaccard | `eval.py:208` | Allows paraphrase, rejects unrelated text |

---

## The 5 Eval Dimensions

All 5 run with no API calls. Verdict: `rate ≥ target` = PASS, `≥ floor` = WARN, else FAIL.

| # | Dimension | Equation | Target / Floor | Scope |
|---|---|---|---|---|
| 1 | Evidence Grounding | `eg_passed / eg_total` | 100% / 95% | All results |
| 2 | Signal Completeness (recall) | `matched / golden_total` | 85% / 75% | Golden only |
| 3 | No Hallucinated Signals (precision) | `matched / predicted_total` | 100% / 95% | Golden only |
| 4 | Type Accuracy | `type_matches / matched_pairs` | 95% / 85% | Matched pairs |
| 5 | Observation Type | `ot_passed / ot_total` | 100% / 98% | All results |

**Shared matcher (#2, #3, #4):** For each golden signal, greedily pick the un-claimed predicted signal with highest evidence overlap; count as `matched` if ≥ 0.5.

**Plain-English translation:**
- **#1** — Does every quote actually appear in the source? (substring match)
- **#2 Recall** — Did we find everything the human found?
- **#3 Precision** — Is everything we found real?
- **#4 Type** — When we agreed a signal exists, did we label it correctly?
- **#5** — Did the code obey the individual/group rule?

---

## Worked Example

Golden has 3 signals, model produces 4, matcher pairs 2, 1 has matching type.

| Metric | Math | Rate |
|---|---|---|
| Recall (#2) | 2 / 3 | 67% |
| Precision (#3) | 2 / 4 | 50% |
| Type Accuracy (#4) | 1 / 2 | 50% |

Same `matched = 2` → different denominator tells a different story.

---

## Reasoning Audit

A separate API call checks whether the model's `reasoning` field actually supports its classifications (type, competencies, confidence).

