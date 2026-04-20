# Lessons — Layer 1 curriculum-agnostic refactor (2026-04-16)

Patterns and corrections that surfaced during the v1 → v2 refactor. These are for future sessions on this project.

## On scoping "reusability" / "curriculum-agnostic"

**Lesson:** When a user asks for "reusable" or "universal" work, don't pick an architecture until you understand which downstream consumer the thing is actually feeding. My first three schema drafts were all wrong because I assumed Layer 1 fed Evolution — it doesn't. Evolution consumes `observation_text + matched_standard_names` directly from the database, not Layer 1's output.

**How to apply:** Before proposing any schema for an intermediate-representation layer, ask (a) who consumes this today, and (b) does consumption exist yet at all. If the answer to (b) is "no, this is the first stage of a future analysis channel we'll figure out later," the right stance is "extract as much honest structure as possible; don't pre-commit to a downstream shape." If there IS a consumer, go read that consumer's input contract first — it dictates the shape.

## On the difference between "curriculum-agnostic" and "truly universal"

**Lesson:** Any taxonomy is a theory. "Developmental domains" (cognitive/social/emotional/physical) is a theory. CASEL is a theory. Even the choice to separate "behavior" from "emotion" as signal types is a theory. There is no view from nowhere. "Curriculum-agnostic" in this project means *doesn't privilege any one school's assessment framework*, not *theoretically neutral* — the latter is impossible.

**How to apply:** When asked to design a "framework-free" schema, be honest about the theoretical commitments you're making (e.g., "these 8 domain descriptors are descriptive not evaluative, but picking 8 is itself a choice"). Don't sell Position C ("universal developmental taxonomy") as Position B ("descriptive metadata") — the user can see through it and it erodes trust.

## On golden.md drift under schema changes

**Lesson:** When the extraction schema changes, the golden annotations don't auto-update. Re-annotating 50 observations by hand is expensive; the better move is to make the eval tolerate drift at the judge level.

**How to apply:** If you're shipping a schema change that affects fields the judge compares, add explicit schema-drift recognition to the judge prompt — e.g., "differences that stem only from schema drift should be flagged as `ambiguous` with `rubric_rule: schema drift`, not as model errors." This lets the pipeline keep running against old goldens while surfacing just the real disagreements. The v2 judge picked up 20 of 23 differences as schema drift on the first run, cleanly separating them from genuine model/golden errors.

## On evidence discipline when "extract as much as possible"

**Lesson:** "Extract as much information as possible" is a prompt that pulls the model toward inference. The line must be held explicitly in the prompt: *more facets per quote is fine; claims the text doesn't support are not*. Nullable facets are the mechanism — `null` is the safe default and should be the most common value for facets that need an explicit textual cue (`agency`, `temporality_cue`).

**How to apply:** When adding optional descriptive facets to an evidence-first schema, always include `null` in the enum and explicitly tell the model in the prompt that `null` is a valid and frequent answer. Without this, models over-commit to values to look thorough.

## On cache invalidation across schema changes

**Lesson:** `extract.py`'s cache key is `SHA256(observation + student_count)` — it does NOT include the prompt. So changing the prompt does not auto-invalidate cached results. Old results from a different schema will still be returned as "cached."

**How to apply:** When changing `prompt.md`, explicitly `rm -rf results/` in the plan. And add a `SCHEMA_VERSION` field to every output JSON so future drift is detectable by just reading a result file. Same for the judge cache (`reasoning_eval/`): any change to `judge_prompt.md` or the fields `build_judge_user_message` emits invalidates all cached judge responses.

## On multi-participant asymmetry

**Lesson:** Pre-v2, an observation like "Diego and Sofia teased Marcos" was mono-subject — all signals implicitly about the formally tagged students. But the recipient's experience (Marcos) was either flattened or invisible. A signal isn't a claim about an observation; it's a claim about a *specific participant in* that observation.

**How to apply:** When designing observation-extraction schemas, always ask: can the same evidence mean different things for different participants in the same event? If yes, the schema needs per-participant attribution (like v2's `participants[].role`). The bullying case is the canonical test — if your schema can't encode "actor-role signals for two students, recipient-role signals for a third unnamed", it's under-expressive.

## On Plan-before-code discipline saving the session

**Lesson:** I wrote the plan to `tasks/todo.md` before touching any code. The plan had 8 phases with per-phase verification gates and rollback paths. When I hit an unexpected block (no `.env.local` / no API key in shell), the plan made it trivial to stop, ask, and resume from exactly the right phase without re-doing prior work.

**How to apply:** For any refactor touching 4+ files or multiple concerns, write a phased plan first. Each phase: goal, steps, verification, rollback. Never skip Phase 0 baselines — they're the diff the user uses to evaluate the change.

## On regex vs. state-machine parsing for messy JSON-ish text

**Lesson:** My first cleanup regex `""([A-Za-z0-9_\-\s]+?)""` for CSV-style doubled-quote escapes in `golden.md` worked on 7 of 9 cases but silently broke on 2 — a case with commas inside the content (`""Once I finish this drawing, I have three more shapes,""`) and cases with triple-quotes at string boundaries (`"""word"""`). Character-class regexes over natural text are brittle: any punctuation or edge-case character breaks them without failing loudly.

**How to apply:** When the input format has even a whisper of irregularity — embedded quotes, nested delimiters, optional fences — don't chain regex substitutions. Write a small character-by-character state machine that tracks context (inside-string / outside-string, current depth, etc.). The state machine in `scripts/migrate_golden.py._escape_doubled_quotes` is ~25 lines and handled every case on the first try. Regex is right for clean tokenization; state machines are right for handling context-dependent transformations.

## On demoting golden-based evaluation

**Lesson:** A hand-annotated golden set has five structural weaknesses that together make it a poor *primary* eval signal for Layer 1: (1) annotation cost doesn't scale across schools, (2) single-annotator ground truth is demonstrably wrong sometimes (the judge flags `golden_wrong` verdicts), (3) schema drift forces re-annotation on every prompt evolution, (4) a static set drifts out of coverage as inputs change, (5) 50 annotations in a 341-record sample is 15% coverage — the other 85% gets no golden signal.

**How to apply:** Use programmatic checks (schema, evidence grounding, derivation rules) plus a reference-free judge as the primary trust signals. Demote golden to a diagnostic tool for investigating specific regressions, not a dashboard metric. Accept that recall (did we miss a signal?) is best covered by rolling human spot-check via a calibration harness — no automated metric answers it honestly. A golden set is still valuable as *annotated reference examples* for prompt iteration, just not as the answer key.

## On cross-family LLM judging

**Lesson:** Using Claude Sonnet to judge Claude Opus output hides self-enhancement bias (documented 5–7% score inflation in recent research). Switching the judge to Gemini 3.1 Pro immediately produced a `model_wrong` verdict on a case the same-family judge had called `ambiguous`. The extractor's output didn't change; only the judge did.

**How to apply:** When designing LLM-as-judge evals, default the judge to a different model family than the producer. On OpenRouter this is a one-line change — no reason not to. Same-family judging should be a deliberate choice with a documented reason, not the default.

## On pydantic at LLM boundaries vs. hand-rolled validation

**Lesson:** The old extract.py validation was a set of required keys plus `isinstance(x, list)` gates. It silently skipped validation for any response where the top-level `signals` wasn't a list. Pydantic at the boundary raises a descriptive error naming the exact field and the expected type — orders of magnitude better for debugging prompt-compliance failures.

**How to apply:** When an LLM response enters your domain logic, parse it through a pydantic model at the boundary. Use `ConfigDict(extra="allow")` at the top level so forward-compatible prompt changes don't hard-fail; keep strict types on required fields. The cost is one file of model definitions; the benefit is that "the extractor stopped returning `language`" becomes immediately visible instead of silently defaulting to `""`.

## On silent skips vs. explicit failures in migration tools

**Lesson:** The first version of `migrate_golden.py` silently returned `None` for un-annotated examples and placeholder rows, producing a final count of 90 examples (50 annotated + 40 un-annotated). But 100 headers exist in the file — the 10 placeholder rows were dropped without being logged.

**How to apply:** In migration / parsing tools, a dropped row must either land in `examples[]`, `parse_errors[]`, or a clearly-documented `skipped[]` array. "Silently skipped" is a data loss mode disguised as success. Even when skips are intentional (as with the placeholder rows here), log them explicitly so the operator can reconcile counts.
