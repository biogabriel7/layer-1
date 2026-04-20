# Synthetic Fixture — Designed Edge Cases

25 observations across 4 primary students + extras. Each observation targets one or more edge cases; this file is the grading rubric for the pipeline's behavior.

## Cast

| student_id | first_last | crew | role in fixture |
|---|---|---|---|
| 1111…1 | Ana López | Year 3 | "stable strength" — reinforcing-heavy |
| 2222…2 | Marcos Ruiz | Year 3 | "trajectory shift" — neutral/mixed → positive |
| 3333…3 | Romeo Martínez | Year 3 | "emerging concern" — positive → negative peer → first concern → 2nd concern |
| 4444…4 | Sofia Smith | Year 3 | ambiguity test (first name collides with Sofia Ramirez and Sofia Peña) |
| aaaa…5 | Sofia Ramirez | Year 3 | ambiguity-trigger student (never tagged) |
| 6666…6 | Diego Fernández | Year 3 | named-differentiation foil |
| 7777…7 | Valentina Gómez | Year 3 | named secondary |
| 8888…8 | Mateo Rojas | Year 3 | padding + secondary |
| 9999…9 | Sofia Peña | Year 4 | cross-crew ambiguity + first-observation |

## Per-observation expectations

| obs | date | tagged | edge case | expected Layer 1.5 behavior |
|---|---|---|---|---|
| 01 | 01-10 | Ana | first-obs for Ana | `tagged`, novelty=null, salience=routine, impact=minimal |
| 02 | 01-12 | Marcos | first-obs, neutral valence | `tagged`, novelty=null, impact=minimal |
| 03 | 01-15 | Romeo | first-obs, named secondary (Valentina) | `tagged`, novelty=null, secondary_participants includes Valentina via first_name_unique_in_crew |
| 04 | 01-18 | Sofia Smith | first-obs, Spanish | `tagged`, Layer 1 extracts in Spanish with language='es', novelty=null |
| 05 | 01-22 | Ana | 2nd obs, same domain/valence as 01 | `tagged`, novelty=reinforcing, salience=routine |
| 06 | 01-25 | Romeo | new domain (task) vs. prior (peer) | novelty=new, salience=notable, impact=moderate |
| 07 | 01-28 | Marcos | mixed valence emotional_indicator | novelty=new (emotional type new), salience=notable |
| 08 | 02-03 | Ana | new domain (peer) for Ana | novelty=new, salience=notable |
| 09 | 02-10 | Romeo | peer domain negative after prior positive peer | novelty=contradicting, salience=significant, impact=high. Diego as secondary. |
| 10 | 02-15 | Ana | reinforcing task+positive | novelty=reinforcing, routine |
| 11 | 02-18 | Marcos | task positive after prior neutral, self-initiated | novelty=reinforcing (prior pattern neutral/mixed), routine |
| 12 | 02-20 | Sofia Peña | first-obs (Year 4) | `tagged`, novelty=null |
| 13 | 02-22 | Romeo | peer positive after prior peer mix (pos obs03 + neg obs09) | LLM judgment: reinforcing or contradicting. Notable either way. |
| 14 | 03-01 | Ana | self-initiated peer reinforcing + secondaries Mateo, Diego | `tagged`, novelty=reinforcing/new, secondaries include Mateo + Diego |
| 15 | 03-05 | Marcos | self-initiated task reinforcing | reinforcing, routine |
| 16 | 03-08 | Romeo | **first-ever concern_flag**, Spanish | novelty=new (concern_flag type), salience=**significant**, impact=**high** |
| 17 | 03-10 | Ana | VERY SHORT vague ("Did well today") | Layer 1 may yield 0 signals or 1 low-confidence; Layer 1.5 record should be empty-signals → impact=minimal |
| 18 | 03-12 | Ana+Marcos+Romeo (3) | group 2-5 with named differentiation | Attribution LLM fires, Ana=actor (helper), Marcos=recipient, Romeo=independent task → per-student signals differ |
| 19 | 03-14 | Ana+Marcos+Romeo (3) | group 2-5 uniform language | Attribution LLM → group_uniform across all three |
| 20 | 03-15 | Ana+Marcos (2) | group 2 with both named | Attribution LLM; either named_match each or group_uniform |
| 21 | 03-16 | 5 tagged (Ana, Marcos, Romeo, Sofia Smith, Diego) | group 2-5, collaborative start + named conflict (Sofia + Diego argue) | Attribution LLM: collaborative signals = group_uniform; argument = named_match to Sofia Smith + Diego |
| 22 | 03-17 | 8 tagged | **6+ group** → deterministic uniform, no LLM | source=group_uniform for all 8, used_attribution_llm=false |
| 23 | 03-18 | Romeo | **second** concern_flag | novelty=reinforcing (concern key already present), salience=**notable** (not significant, since prior_concern_flag_count>0), impact=moderate |
| 24 | 03-20 | Ana+Marcos (2) | "Sofia" mentioned, two Year-3 Sofias → ambiguous → LLM disambiguates | Attribution LLM fires, secondary_participants resolves "Sofia" to one candidate with match=llm_resolved |
| 25 | 03-22 | Ana+Marcos (2) | "Luka" mentioned, not in roster → unresolved | secondary_participants does NOT include Luka |

## Per-student cumulative expectations (after run)

- **Ana**: ~8 single-student records + 5 group records. Mostly routine/reinforcing. 1 or 2 notable for new domains. impact distribution: mostly minimal, few moderate.
- **Marcos**: ~5 single-student + 5 group. Mix of novelty transitions. impact distribution: mostly minimal/moderate.
- **Romeo**: ~8 records total. Includes the `contradicting` at obs 09 (high impact), the `significant` concern at obs 16 (high), and a `notable` concern at obs 23 (moderate). The clearest "this student needs attention" signal in the fixture.
- **Sofia Peña**: 1 record, novelty=null, routine, impact=minimal. Sanity-check of first-obs path.

## Attribution path coverage

- `tagged` (single-student, deterministic): obs 01–17, 23 (17 observations)
- `named_match` (2-5 group, LLM): obs 18, 20, 21 (parts)
- `group_uniform` (2-5 LLM): obs 19, 21 (parts)
- `group_uniform` (6+ deterministic): obs 22
- Attribution LLM triggered via secondary-only ambiguity (1-student + ambiguous name): obs 24's variant is 2-student, but covered. (No single-student-with-ambiguous-secondary in this fixture.)

## Secondary-participant coverage

- `first_name_unique_in_crew` deterministic: obs 03 (Valentina), obs 09 (Diego), obs 14 (Mateo + Diego)
- `llm_resolved` ambiguous: obs 24 (Sofia)
- unresolved (dropped): obs 25 (Luka)

## Bilingual coverage

- English: most
- Spanish: obs 04, 16

## Signal type coverage

- behavioral_evidence: most observations
- emotional_indicator: obs 07 (mixed), obs 13 (positive)
- context_marker: implicit in many (recess, lunch, field trip, etc.)
- concern_flag: obs 16, 23

## Valence coverage

- positive: most
- negative: obs 09, 16, 23
- mixed: obs 07
- neutral: obs 02

## What we're NOT testing here

- Cross-family LLM judge evaluation (future follow-up)
- Attendance gaps / disengagement detection (Layer 3 territory)
- Real-world noisy transcription / OCR errors
- Very long observations (1,000+ chars)
