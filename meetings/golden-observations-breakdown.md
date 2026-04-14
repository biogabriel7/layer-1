# Golden Dataset: Observation Breakdown

Based on the 100 examples in `golden.md`.

---

## By Observation Type (Student Count)

| Type | Count | Examples |
|---|---|---|
| **Individual** (student_count = 1) | 82 | #1-7, #10-24, #33-55, #57-66, #68-72, #74-76, #78-80, #82-89, #91-93, #95-100 |
| **Group** (student_count > 1) | 18 | #8 (4), #9 (4), #25 (6), #26 (21), #27 (15), #28 (15), #29 (14), #30 (13), #31 (12), #32 (12), #67 (2), #73 (3), #77 (8), #81 (5), #86 (5), #90 (25), #94 (16), #98 (4) |

Group sizes range from 2 to 25 students.

---

## By Content Category

### Minimal / Vague Observations (11 examples)
Short, non-specific observations with little or no actionable detail.

| # | Observation | Notes |
|---|---|---|
| 1 | "Good participation today." | Evaluative, no evidence |
| 2 | "No Comment" | Empty |
| 5 | "Did well on the math test." | Vague positive |
| 7 | "N/A" | Empty |
| 43 | "He did okay today." | Vague |
| 44 | "She was fine during class." | Vague |
| 45 | "Average performance this week." | Vague |
| 46 | "Nothing notable to report." | Vague |
| 47 | "Continues to make progress." | Vague |
| 74 | "She did a great job on the project..." | Evaluative, no concrete evidence |
| 75-76 | "Absent today." / "See previous notes." | Non-observations |

### Academic Performance (14 examples)
Focus on academic skills, test results, and subject-matter competency.

Examples: #5, #12, #13, #14, #15, #16, #29, #30, #31, #48, #53, #54, #59, #60

Key subjects covered: math, reading, writing, science, geography, geometry

### Behavioral Concerns (10 examples)
Observable problematic behaviors — refusal, aggression, disruption, disengagement.

Examples: #4, #6, #17, #19, #22, #24, #65, #68, #87, #96

Patterns: refusal to participate, physical aggression, withdrawal, repeated disruption

### Emotional Indicators (8 examples)
Observations centered on affect, emotional state, or distress.

Examples: #3, #18, #20, #21, #49, #61, #66, #71

Includes: anxiety, frustration, crying, disappointment, joy, pride

### Social-Emotional & Relationship Skills (15 examples)
Collaboration, empathy, conflict resolution, helping others, inclusion.

Examples: #8, #25, #51, #52, #62, #67, #69, #81, #82, #84, #86, #89, #95, #99, #100

### Self-Management & Regulation (10 examples)
Goal-setting, independence, routines, self-calming, persistence.

Examples: #50, #55, #61, #63, #72, #83, #88, #92, #93, #97

### Group Learning Activities (10 examples)
Whole-class or large-group instructional observations.

Examples: #9, #26, #27, #28, #30, #31, #32, #77, #90, #94

### Rich / Multi-Signal Observations (12 examples)
Long, detailed observations with multiple signal types in a single entry.

Examples: #10, #11, #38, #39, #41, #55, #80, #84, #89, #92, #96, #100

These are the most complex extraction targets — they contain 4+ signals spanning multiple types and SEL competencies.

### Mixed Positive-Negative (7 examples)
Observations that contain both strengths and concerns in the same entry.

Examples: #33, #34, #35, #36, #37, #80, #96

Important for testing the pipeline's ability to extract both positive and negative signals from a single observation.

### Inquiry & Curiosity-Driven (7 examples)
Observations focused on exploration, scientific thinking, and student-driven learning.

Examples: #26, #38, #56, #57, #58, #79, #91

---

## Summary Statistics

| Metric | Value |
|---|---|
| Total examples | 100 |
| Individual observations | 82 (82%) |
| Group observations | 18 (18%) |
| Minimal/vague (edge cases) | 11 (11%) |
| Rich multi-signal | 12 (12%) |
| Mixed positive-negative | 7 (7%) |
| Longest observation | #10 (Romeo, ~150 words) |
| Shortest observations | #7 "N/A", #75 "Absent today." |

---

## Coverage Requirements

| Category | Min Required | Actual Count | Examples | Status |
|---|---|---|---|---|
| Very short (<100 chars) | 5+ | 18 | #1-7, #8, #43-47, #75, #76, #82, #83, #90 | Pass |
| Long (>400 chars) | 15+ | 17 | #10, #11, #26, #28, #38, #39, #41, #55, #56, #80, #86, #89, #92, #96, #98, #99, #100 | Pass |
| Concern flag | 10+ | 14 | #4, #6, #11, #17-24, #65, #68, #87 | Pass |
| Group (student_count > 1) | 10+ | 19 | #8, #9, #25-32, #56, #67, #73, #77, #81, #86, #90, #94, #98 | Pass |
| Mixed positive/negative | 5+ | 14 | #10, #11, #24, #33-37, #63, #68, #80, #92, #96, #98 | Pass |
| Purely academic (no SEL) | 5+ | 10 | #5, #12-16, #29, #53, #54, #59 | Pass |
| Multi-signal high-density (4+) | 5+ | 39 | #10, #11, #17-19, #21, #22, #24, #26-28, #33-42, #51, #52, #55, #56, #68, #71, #73, #80, #84-86, #89, #92, #96-100 | Pass |
| Vague/low-density (0-1 signals) | 5+ | 14 | #1-3, #5, #7, #43-47, #74-76, #90 | Pass |

All 8 coverage categories pass with comfortable margins above minimums.

---
