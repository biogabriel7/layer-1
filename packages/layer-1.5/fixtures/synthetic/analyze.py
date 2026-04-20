"""Grade the synthetic-fixture run against EXPECTATIONS.md."""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "outputs" / "contextualizations.jsonl"
ROSTER = ROOT / "roster.json"
OBS = ROOT / "observations.json"

records = [json.loads(line) for line in OUT.read_text().splitlines() if line.strip()]
roster = {s["student_id"]: s for s in json.loads(ROSTER.read_text())}
observations = {o["observation_id"]: o for o in json.loads(OBS.read_text())}


def _name(sid: str) -> str:
    s = roster.get(sid, {})
    return f"{s.get('first_name', '?')} {s.get('last_name', '?')}"


def _short(oid: str) -> str:
    return oid[:8]


by_obs: dict[str, list[dict]] = defaultdict(list)
for r in records:
    by_obs[r["source"]["observation_id"]].append(r)


def _check(label: str, cond: bool, detail: str = "") -> None:
    mark = "✓" if cond else "✗"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))


# ── 1. Counts ──────────────────────────────────────────────────────────
print(f"records written: {len(records)}  (was 43 pre-changes)")
roles = Counter(r["source"].get("role") for r in records)
print(f"roles emitted: {dict(roles)}")
attrib = Counter(r["attribution"]["source"] for r in records)
print(f"attribution sources: {dict(attrib)}")
print(f"attribution LLM fired on {sum(1 for r in records if r['used_attribution_llm'])} records")

# ── 2. Recipient-aware attribution: obs 18 ─────────────────────────────
print("\n=== obs 18 (Ana helped Marcos while Romeo worked) ===")
obs18 = by_obs.get("obs00018-0000-4000-a000-000000000018", [])
for r in obs18:
    sid = r["source"]["student_id"]
    role = r["source"].get("role")
    n = len(r["contextualized_signals"])
    src = r["attribution"]["source"]
    print(f"  {_name(sid):<22} role={role:<12} signals={n} attrib={src}")

marcos = "22222222-2222-4222-a222-222222222222"
obs18_marcos = [r for r in obs18 if r["source"]["student_id"] == marcos]
marcos_shape = [
    (r["source"].get("role"), len(r["contextualized_signals"]))
    for r in obs18_marcos
]
_check(
    "obs18 Marcos has a record with role=recipient (was empty pre-fix)",
    any(r["source"].get("role") == "recipient" for r in obs18_marcos),
    f"marcos records={marcos_shape}",
)

# ── 3. Language passthrough ────────────────────────────────────────────
print("\n=== Language passthrough ===")
langs = Counter(r.get("language") for r in records)
print(f"  records by language: {dict(langs)}")
spanish_obs = {
    "obs00004-0000-4000-a000-000000000004",  # Sofia Smith Spanish
    "obs00016-0000-4000-a000-000000000016",  # Romeo concern Spanish
}
spanish_records = [r for r in records if r["source"]["observation_id"] in spanish_obs]
_check(
    "Spanish observations carry language='es' through Layer 1.5",
    all(r.get("language") == "es" for r in spanish_records),
    f"spanish records' languages: {Counter(r.get('language') for r in spanish_records)}",
)

# ── 4. profile_impact single field (no rollup duplicate) ───────────────
has_rollup = any("profile_impact_rollup" in r for r in records)
_check(
    "profile_impact_rollup field removed from output",
    not has_rollup,
)

# ── 5. History split ──────────────────────────────────────────────────
print("\n=== History split: individual vs group ===")
for r in records[:3]:
    h = r["history_summary"]
    print(f"  {_short(r['source']['observation_id'])} {_name(r['source']['student_id']):<22} "
          f"prior_sigs={h['prior_signal_count']:<2} "
          f"indiv={h['prior_individual_signal_count']:<2} "
          f"group={h['prior_group_signal_count']:<2}")

# Any record where the sum matches total
mismatches = sum(
    1 for r in records
    if r["history_summary"]["prior_signal_count"]
    != (r["history_summary"]["prior_individual_signal_count"]
        + r["history_summary"]["prior_group_signal_count"])
)
_check(
    "prior_individual + prior_group == prior_signal_count (always)",
    mismatches == 0,
    f"mismatches={mismatches}",
)

# ── 6. Enriched snippets ──────────────────────────────────────────────
enriched_examples = [
    snip
    for r in records
    for snip in r["history_summary"]["recent_evidence_snippets"]
]
has_type = sum(1 for s in enriched_examples if "type" in s)
has_valence = sum(1 for s in enriched_examples if "valence" in s)
_check(
    "recent_evidence_snippets carry facet tags (type/valence/primary_domain)",
    has_type == len(enriched_examples) and has_valence == len(enriched_examples),
    f"{has_type}/{len(enriched_examples)} snippets have type; {has_valence} have valence",
)

# ── 7. Narrative grounding ─────────────────────────────────────────────
def narrative_grounded(r: dict) -> bool:
    n = r["narrative"]
    h = r["history_summary"]
    # Contains a count from history_summary
    for key in ("prior_observation_count", "prior_signal_count",
                "prior_individual_signal_count", "prior_group_signal_count",
                "prior_concern_flag_count"):
        if h[key] > 0 and str(h[key]) in n:
            return True
    # Contains a spelled-out count ("first", "second", "third" ... )
    lower_n = n.lower()
    for word in ("first", "second", "third", "fourth", "fifth"):
        if word in lower_n:
            return True
    # Contains a verbatim quote
    if n.count('"') >= 2:
        return True
    return False

grounded = sum(1 for r in records if narrative_grounded(r))
_check(
    "≥80% of narratives contain a history count or verbatim quote",
    grounded / len(records) >= 0.80,
    f"{grounded}/{len(records)} = {grounded*100/len(records):.0f}%",
)

# ── 8. Rubric carry-overs from v1 ──────────────────────────────────────
romeo = "33333333-3333-4333-a333-333333333333"
romeo_records = sorted(
    (r for r in records if r["source"]["student_id"] == romeo),
    key=lambda r: r["source"]["created_at"],
)
# Find the first observation where Romeo had a concern_flag signal in Layer 1.
# Whichever one it is should be flagged significant+high. Subsequent concerns
# should drop to notable.
romeo_with_concern: list[dict] = []
for r in romeo_records:
    h = r["history_summary"]
    # Heuristic: a record's first-ever concern is identifiable by
    # prior_concern_flag_count == 0 AND any salience == 'significant'
    if h["prior_concern_flag_count"] == 0 and any(
        s["salience"] == "significant" for s in r["contextualized_signals"]
    ):
        romeo_with_concern.append(r)
        break

detail = (
    _short(romeo_with_concern[0]["source"]["observation_id"])
    if romeo_with_concern else "NONE"
)
_check(
    "Romeo's first concern_flag observation → significant + high",
    bool(romeo_with_concern)
    and romeo_with_concern[0]["profile_impact"] == "high",
    f"first-significant record: {detail}",
)

# Second/subsequent concern flags should be notable, not significant.
later_concerns = [
    r for r in romeo_records
    if r["history_summary"]["prior_concern_flag_count"] > 0
    and any(s["salience"] in ("notable", "significant") for s in r["contextualized_signals"])
]
_check(
    "Later concern_flag records → notable, not significant",
    bool(later_concerns)
    and all(
        all(s["salience"] != "significant" for s in r["contextualized_signals"]
            if "concern" in (s.get("reasoning") or "").lower())
        for r in later_concerns
    ),
)

obs22 = by_obs.get("obs00022-0000-4000-a000-000000000022", [])
_check(
    "obs22 (8-student group): all group_uniform, no attribution LLM",
    len(obs22) == 8
    and all(r["attribution"]["source"] == "group_uniform" for r in obs22)
    and all(not r["used_attribution_llm"] for r in obs22),
)

# ── 9. Per-student summary ────────────────────────────────────────────
print("\n=== Per-student rollup (records, signals, impact dist, role dist) ===")
by_student: dict[str, list[dict]] = defaultdict(list)
for r in records:
    by_student[r["source"]["student_id"]].append(r)
for sid, rs in sorted(by_student.items(), key=lambda kv: _name(kv[0])):
    n_sigs = sum(len(r["contextualized_signals"]) for r in rs)
    impacts = Counter(r["profile_impact"] for r in rs)
    role_dist = Counter(r["source"].get("role") for r in rs)
    print(f"  {_name(sid):<22} recs={len(rs):<2} sigs={n_sigs:<2} "
          f"impact={dict(impacts)} roles={dict(role_dist)}")
