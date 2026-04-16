# Golden Dataset: Observation Breakdown

Based on the 100 examples in `golden.md`.

---

## Summary Statistics

| Metric | Value |
|---|---|
| Total examples | 100 |
| Individual observations | 82 (82%) |
| Group observations | 18 (18%) |
| Very short (<100 chars) | 18 |
| Long (>400 chars) | 17 |
| Concern flags | 14 |
| Mixed positive-negative | 14 |
| Purely academic (no SEL) | 10 |
| Multi-signal high-density (4+) | 39 |
| Vague/low-density (0-1 signals) | 14 |

---

## Summary Statistics — First 50 Examples

| Metric | Value |
|---|---|
| Total examples | 50 |
| Individual observations | 40 (80%) |
| Group observations | 10 (20%) |
| Very short (<100 chars) | 12 |
| Long (>400 chars) | 7 |
| Concern flags | 12 |
| Mixed positive-negative | 6 |
| Purely academic (no SEL) | 9 |
| Multi-signal high-density (4+) | 12 |
| Vague/low-density (0-1 signals) | 16 |

---

## Edge Cases

Edge cases are observations that probe the boundaries of the prompt rules — places where the correct extraction is non-obvious and a naive model is likely to fail. Categories below are tied to specific rules in `prompt.md`.

### Edge Cases in the First 50 Examples

| # | Observation (excerpt) | Edge case category | What makes it tricky |
|---|---|---|---|
| 2 | `"No Comment"` | Empty/meaningless content (Rule 6) | Must return `"signals": []` — no signal even though there is text. |
| 7 | `"N/A"` | Empty/meaningless content (Rule 6) | Same as #2 — tests that model doesn't invent content from a stub. |
| 46 | `"Nothing notable to report."` | Empty/meaningless content (Rule 6) | Fluent filler with zero behavioral content — must return empty array, not a low-confidence signal. |
| 1, 43–45, 47 | `"Good participation today."` / `"He did okay today."` / `"Average performance this week."` | Evaluative-only, no observable action (Confidence rules) | Model must extract a single `behavioral_evidence` at `low` confidence — resist inventing SEL competencies from vague praise. |
| 8 | Group=4: `"Her commitment to collaborative learning is evident..."` | Evaluative phrase for a group with no observable action | Pure judgment language. Golden keeps `relationship_skills` but pins confidence to `low`. |
| 9 | Group=4: `"One student took the lead in mixing the ingredients while others shaped the structure."` | Unnamed actor in group observation (Rule 8) | Confidence capped at `medium` because "one student" / "others" can't be attributed. |
| 10 | Andrei: "he was able to express that he was feeling overwhelmed" | Student-expressed emotion (Rule 3 exception) | Emotion must stay as `emotional_indicator` because the student self-reported it, not the teacher inferring it. |
| 11 | George: `"he is still developing his ability to manage frustration..."` | Capability / future-tense framing (Rule 9) | Pins confidence to `low` — capability statement paired with prior observed incident. |
| 14 | `"He is beginning to understand longitude and latitude coordinates."` | Capability statement (Rule 9) | "Is beginning to" — extractable but confidence capped at `medium` (not `high`). |
| 17, 18, 20, 22, 24 | Marcus "consistently late… refused…"; Lily "third time this week"; Noah "repeatedly… three of the last four sessions" | Concern threshold language (Rule 10) | Trigger words `consistently`, `repeatedly`, `third time`, `refused` escalate routine struggle into `concern_flag`. |
| 17, 18, 20, 22, 24 | Same observations as above | Pattern+incident merged into single signal (Rule 2) | Multi-sentence pattern must stay one signal so recurrence context isn't lost. |
| 19 | Ethan: "he told me he was angry because someone took his spot" | Student-expressed emotion alongside concern behavior (Rule 3 exception + Rule 5) | Pushing/kicking = `concern_flag`; the self-reported anger is a separate `emotional_indicator` with `self_awareness`. |
| 21 | Sofia: "Before every test... shaking her hands and breathing rapidly" | Somatic anxiety markers — not a clinical label | Concern without diagnosing — model must NOT infer "anxiety disorder" (What NOT to Extract). |
| 27 | Group=15: "Most students told me that the game was fun... but some said it was stressful" | Conflicting unnamed subgroups (Rule 8) | Do NOT extract — no attributable subject. Golden skips this sentence. |
| 27, 28 | `"we acknowledged that focus is an important skill..."` | Teacher reflection on lesson value (What NOT to Extract) | Excluded — describes teacher framing, not student behavior. |
| 33–37 | Elena, Oscar, Priya, James, Zara | Mixed positive-negative (Rule 5) | Both positive behaviors and concerns extracted separately from same observation. |
| 34 | Oscar: `"showed great initiative by volunteering to be the group leader"` | Observable over evaluative (Rule 3) | Golden extracts only `"volunteering to be the group leader"` — drops the `showed great initiative` judgment. |
| 38 | Kai: `"Kai demonstrated exceptional curiosity"` paired with `"asking questions about every plant species"` | Borderline Rule 3 case | Golden keeps both — the judgment becomes `emotional_indicator`, the action becomes separate `behavioral_evidence`. Tests whether model over-prunes. |
| 48 | `"He is developing strong problem-solving..."` / `"He can observe how..."` | Capability statement without paired action (Rule 9) | `medium` confidence ceiling; model should not elevate to `high` despite concrete-sounding verbs. |

### Additional Edge Cases in Examples 51–100

The second half of the set introduces several new edge-case patterns beyond those in the first 50. Cases below are the novel ones — the first-50 categories (empty content, concern threshold, mixed valence, capability statements, student-expressed emotion) also recur here.

| # | Observation (excerpt) | Edge case category | What makes it tricky |
|---|---|---|---|
| 73 | Group=3: Maria, Carlos, Sofia each get their own actions | Multiple named students in one observation (Rule 7) | Each named student yields separate signals — model must not collapse into generic "the group" signals. |
| 74 | `"I think she has a lot of potential. I hope she continues to work hard..."` | Teacher hopes/predictions + character judgments (What NOT to Extract) | Entire observation is hopes, potential, judgments — the extractable surface is almost nothing. High risk of hallucinated signals. |
| 75 | `"Absent today."` | Attendance-only stub | Edge of Rule 6 — arguably a context marker, arguably meaningless. Tests consistency of empty-vs-context_marker decision. |
| 76 | `"See previous notes."` | Reference-only content (Rule 6) | No observable content — must return `"signals": []`. |
| 78 | `"At the beginning of the year, he could barely write... Now he consistently produces paragraphs..."` | Longitudinal/retrospective progress comparison | Confidence calibration is tricky: remembered "beginning of year" state vs. current "consistently" evidence — model must not over-merge. |
| 80 | Birthday day with high-engagement AM, careless PM, elaborate art session | Within-day valence shift across multiple contexts (Rule 5) | Must split into multiple context_markers + mixed-valence signals without collapsing the day into a single summary. |
| 82 | `"She raised her hand before speaking every time today and waited to be called on."` | Very short but concrete / single high-confidence signal | Short length but `high` confidence — tests that brevity ≠ low confidence. |
| 83 | `"He can now tie his shoes independently and does so without reminders."` | Capability + paired observed action (Rule 9) | "Can now tie" is a capability; "does so without reminders" is observed action. Golden keeps the observed action; capability alone would cap at `low`. |
| 86 | Group=5: `"another student suggested... the group agreed... their classmate"` | Unnamed actor chain in group observation (Rule 8) | "Another student", "the group", "their classmate" are unattributable — confidence ceiling `medium`. |
| 87 | `"She has been excluded from play groups by the same three students repeatedly this month."` | Concern threshold: social-exclusion pattern (Rule 10) | `repeatedly`, `this month` — crosses from isolated incident into flaggable pattern. |
| 90 | Group=25: `"The class went on a field trip to the science museum today."` | Pure context, no student behavior | Only a `context_marker`; no behavioral, emotional, or concern signals to extract. Tests resistance to over-extraction. |
| 92 | Pottery: `"he was visibly upset"` (observed) + `"he was proud"` (observed) + `"he learned that mistakes help you get better"` (student self-report) | Mixed observed-vs-reported emotional signals | "Visibly upset" is teacher-observed emotion; "said he had worked so hard" and the final reflection are student-expressed. Golden treats each with different confidence anchors. |
| 96 | First half engaged → after lunch "had to be removed... threw materials" → "apologized to the class on his own initiative" | Three-phase valence shift + apology (Rule 5) | Single observation spans positive → concern → restorative action. Model must extract all three without letting one phase dominate. |
| 98 | Group=4: `"Two members did most of the work while the other two contributed very little"` | Unnamed subgroup split attribution (Rule 8) | Two subgroups with conflicting effort levels — ambiguous whether extractable; when extracted, confidence caps at `medium`. |
| 100 | End-of-year reflection recalling "flipped a desk" incident from October | Historical concern + current growth in student self-report | The recalled incident is not a current concern_flag — it's the student reflecting on past behavior. Tests whether the model mis-tags retrospective references as fresh concerns. |

**Novel edge-case categories introduced in 51–100:**
- Multiple named students (Rule 7): #73
- Teacher hopes/predictions dominating the whole text (What NOT to Extract): #74
- Attendance-only / reference-only stubs: #75, #76
- Longitudinal/retrospective comparisons: #78, #100
- Within-day multi-phase valence shifts: #80, #96
- Pure-context observations with no student behavior: #90
- Unnamed subgroup split attribution (vs. conflicting subgroups in #27): #98

---
