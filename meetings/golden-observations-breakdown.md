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

## Estimated Signal Breakdown Per Example

Best-guess signal count and type distribution for each observation.

**Signal types:** BE = behavioral_evidence, EI = emotional_indicator, CM = context_marker, CF = concern_flag

| # | Est. Signals | BE | EI | CM | CF | Notes |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | | | | Vague "good participation" |
| 2 | 0 | | | | | "No Comment" — empty |
| 3 | 1 | 1 | | | | Ambiguous — quiet could be concern |
| 4 | 2 | 1 | | | 1 | Refusal + "again" pattern |
| 5 | 1 | 1 | | | | Vague academic |
| 6 | 2 | 1 | | | 1 | Present but disengaged |
| 7 | 0 | | | | | "N/A" — empty |
| 8 | 2 | 1 | | 1 | | Collaboration + project context |
| 9 | 4 | 3 | | 1 | | Divided tasks, communicated, one led mixing |
| 10 | 7 | 3 | 2 | 1 | 1 | Refused, joined, had fun, can't find place, encouraged |
| 11 | 5 | 2 | 2 | | 1 | Disengaged, understood after support, frustrated, cried |
| 12 | 2 | 2 | | | | Completed problems, showed work |
| 13 | 2 | 2 | | | | Read aloud, answered questions |
| 14 | 3 | 3 | | | | Identified continents, labeled oceans, beginning coordinates |
| 15 | 2 | 2 | | | | Sorted shapes, needed guidance |
| 16 | 2 | 2 | | | | Wrote paragraph, accurate spelling/punctuation |
| 17 | 4 | 1 | | 1 | 2 | Late pattern, head down, not responding, refuses |
| 18 | 4 | 1 | 1 | 1 | 1 | Sat alone, cried, no friends, third time this week |
| 19 | 4 | 1 | 1 | | 2 | Pushed student, argued, kicked chair, explained anger |
| 20 | 4 | 1 | 1 | 1 | 1 | Level dropped, avoids reading, hates reading, flips pages |
| 21 | 5 | 1 | 2 | 1 | 1 | Bathroom requests, shaking, breathing, completed with support |
| 22 | 4 | 1 | | 1 | 2 | Told partner slow, grabbed book, refused, repeated pattern |
| 23 | 3 | 1 | | 1 | 1 | Stopped raising hand, stares, "everything is fine" |
| 24 | 4 | 2 | | | 2 | Interrupted, left spot, knocked bottle, apologized but continued |
| 25 | 3 | 3 | | | | Discussed democratically, took turns, resolved conflict |
| 26 | 4 | 3 | | 1 | | Matched scents, created model, discussed connections |
| 27 | 4 | 2 | 1 | 1 | | Strategic thinking, mixed feelings, collaboration |
| 28 | 4 | 2 | | 1 | 1 | Focus game, more focused, participated, acknowledged importance |
| 29 | 1 | 1 | | | | Exploring fractions |
| 30 | 2 | 2 | | | | Independent learning, applied knowledge |
| 31 | 3 | 2 | 1 | | | Explored patterns, discovered rules, enthusiastic |
| 32 | 3 | 1 | 2 | | | Gave feedback, felt happy, proud to present |
| 33 | 4 | 2 | | | 2 | Enthusiastic art, refused cleanup, said painting ugly |
| 34 | 5 | 3 | 1 | | 1 | Volunteered, organized, frustrated, dismissed, acknowledged |
| 35 | 4 | 2 | | | 2 | Excelled math, helped classmates, argument, refused PE |
| 36 | 4 | 2 | | | 2 | Good essay, focused, then distracting, moved twice |
| 37 | 4 | 2 | | | 2 | Led debate, listened, blamed teammates |
| 38 | 7 | 5 | 1 | 1 | | Sketched, shared, self-encouraged, helped, "best day" |
| 39 | 7 | 4 | 1 | | | Chose topic, planned, read aloud first time, accepted feedback, felt proud |
| 40 | 4 | 4 | | | | Designed experiment, explained findings, helped student |
| 41 | 7 | 5 | 1 | | | Followed recipe, measured, waited, cleaned spill, tasted, suggested |
| 42 | 5 | 4 | | | | Presented, eye contact, answered questions, recommended, created cover |
| 43 | 0 | | | | | "He did okay today" — vague |
| 44 | 0 | | | | | "She was fine during class" — vague |
| 45 | 0 | | | | | "Average performance this week" — vague |
| 46 | 0 | | | | | "Nothing notable to report" — empty |
| 47 | 0 | | | | | "Continues to make progress" — vague |
| 48 | 2 | 2 | | | | Building structures, observing dome stability |
| 49 | 3 | 1 | 1 | | | Disappointed, knew she could do better, asked to retake |
| 50 | 4 | 4 | | | | Set goal, tracked progress, adjusted target, finished early |
| 51 | 5 | 5 | | | | Listened, mediated, proposed compromise, ensured roles, checked in |
| 52 | 4 | 3 | 1 | | | Brought wallet, explained reasoning, waited, genuinely happy |
| 53 | 2 | 2 | | | | Mastered above grade level, solved independently |
| 54 | 2 | 1 | | | 1 | Beginning letter sounds, needs support with pencil |
| 55 | 6 | 4 | 1 | | | Curiosity food pyramid, tried flavors, leadership cooking, math skills, awareness |
| 56 | 4 | 3 | 1 | | | Curiosity, investigated illusions, questions, understanding |
| 57 | 2 | 1 | 1 | | | Enjoyed hero's journey, eager for twists |
| 58 | 3 | 2 | | | | Built circuits, trial and error, growing understanding |
| 59 | 2 | 2 | | | | Measured sides/angles, understanding of geometry |
| 60 | 2 | 2 | | | | Observing nature structures, developing understanding |
| 61 | 4 | 2 | 2 | | | Felt overwhelmed, used breathing, counted to ten, said it helped |
| 62 | 3 | 3 | | | | Noticed new student, invited, introduced, asked about games |
| 63 | 5 | 3 | 2 | | | Struggled, wanted to give up, came back, completed 4/6, felt better |
| 64 | 3 | 3 | | | | Participated, shared ideas, identified characters/conflict |
| 65 | 3 | 1 | | | 2 | Difficulty concentrating, got up, didn't complete exercises |
| 66 | 3 | 1 | 1 | | | Enthusiastic, painting makes her happy, shared materials |
| 67 | 3 | 2 | | 1 | | Disagreement, used timer, followed through |
| 68 | 5 | 2 | | 1 | 2 | Threw blocks, screamed, 15 min to calm, completed worksheet, daily pattern |
| 69 | 3 | 3 | | | | Finished early, sat with student, walked through steps |
| 70 | 3 | 2 | 1 | | | Kept beat, smiled, asked to practice |
| 71 | 4 | 3 | 1 | | | Participated, cheered, congratulated, tripped and kept going |
| 72 | 3 | 3 | | | | Worked independently 45 min, used index, took notes |
| 73 | 4 | 3 | | 1 | | Maria intro'd, Carlos data, Sofia Q&A, all rehearsed |
| 74 | 0 | | | | | Evaluative, no concrete evidence |
| 75 | 0 | | | 1 | | "Absent today" — context only |
| 76 | 0 | | | | | "See previous notes" — empty |
| 77 | 4 | 3 | | 1 | | Presented arguments, respected limits, acknowledged points, voted |
| 78 | 4 | 4 | | | | Sentence→paragraphs, spelling improved, uses dictionary, handwriting |
| 79 | 3 | 3 | | | | Noticed textures, described, listened and counted birds |
| 80 | 6 | 3 | 1 | 1 | 1 | Excited birthday, shared cupcakes, thanked by name, unfocused math, drawing, asked to keep |
| 81 | 3 | 2 | 1 | | | Encouraged each other, "it's okay," celebrated together |
| 82 | 1 | 1 | | | | Raised hand, waited to be called |
| 83 | 1 | 1 | | | | Ties shoes independently |
| 84 | 5 | 5 | | | | Listened, raised hand, proposed compromise, understood both sides, thanked |
| 85 | 5 | 3 | 1 | | | Asked what to improve, identified confusion, "I can do better," made study plan, asked parents |
| 86 | 5 | 4 | | | 1 | Overlooked student, suggested role, helped practice, performed successfully, cheered |
| 87 | 3 | 1 | 1 | | 1 | Excluded repeatedly, told "can't play," sat alone |
| 88 | 3 | 3 | | | | Unpacked, organized, started journal, turned in homework, watered plant |
| 89 | 6 | 4 | 1 | | | Noticed teasing, confronted, sat with student, conversation, relieved, explained motivation |
| 90 | 1 | | | 1 | | "Field trip to science museum" — context only |
| 91 | 3 | 3 | | | | Used iPad, bookmarked sources, took notes, asked for help |
| 92 | 5 | 3 | 2 | | | Shaped carefully, upset when cracked, started over, proud, learned from mistakes |
| 93 | 2 | 2 | | | | Followed routine chart, checked chart multiple times |
| 94 | 3 | 2 | | 1 | | Created concept map, contributed ideas, resolved differences |
| 95 | 2 | 1 | 1 | | | Thanked teacher, said it helped |
| 96 | 7 | 3 | 1 | 1 | 2 | Engaged, insightful, behavior shifted, argumentative, threw materials, apologized |
| 97 | 4 | 4 | | | | Recognized falling behind, asked for help, pointed out confusion, completed |
| 98 | 5 | 2 | | 1 | 2 | Unequal work, didn't understand role, redistributed, incomplete, reflected |
| 99 | 6 | 5 | 1 | | | Organized schedules, created document, calm under pressure, encouraged, congratulated |
| 100 | 6 | 3 | 2 | 1 | | Wrote about controlling temper, recalled incident, thanked, set goal, more confident |

### Signal Type Totals (estimated)

| Signal Type | Est. Count | % of Total |
|---|---|---|
| behavioral_evidence | 219 | 67% |
| emotional_indicator | 38 | 12% |
| context_marker | 26 | 8% |
| concern_flag | 43 | 13% |
| **Total** | **326** | **100%** |

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

## Key Takeaways for Extraction Quality

1. **Edge cases matter** — 11% of observations are vague or empty; the pipeline must handle these gracefully (zero or minimal signals).
2. **Mixed observations are a precision test** — examples like #33-37 and #96 require extracting both positive and negative signals without merging them.
3. **Group vs. individual split (~82/18)** mirrors the full dataset distribution noted in the project docs (~81/19).
4. **Multi-signal observations** (#10, #38, #39, etc.) are the hardest extraction targets and test signal completeness most rigorously.
5. **No Spanish-language examples** in the golden set, despite the full dataset being bilingual.
