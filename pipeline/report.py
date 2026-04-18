"""Terminal-report formatters for programmatic metrics and the audit."""

from pipeline.models import (
    AUDIT_TARGET,
    TARGETS,
    AuditCheckResult,
    AuditMetrics,
    Metrics,
)

SHIPPABILITY_TARGET: tuple[float, float] = (0.95, 0.85)

_RowList = list[tuple[str, float, tuple[float, float], str]]


def pct(num: int, den: int) -> float:
    return 0.0 if den == 0 else num / den


def verdict(rate: float, target: float, floor: float) -> str:
    if rate >= target:
        return "PASS"
    if rate >= floor:
        return "WARN"
    return "FAIL"


def metrics_rows(m: Metrics) -> _RowList:
    eg_failed_obs = {k for (k, _ev) in m.eg_failures}
    ship_passed = m.ot_total - len(eg_failed_obs)
    rows: _RowList = [
        ("Evidence Grounding", pct(m.eg_passed, m.eg_total),
         TARGETS["evidence_grounding"], f"{m.eg_passed}/{m.eg_total} signals"),
        ("Observation Type", pct(m.ot_passed, m.ot_total),
         TARGETS["observation_type"], f"{m.ot_passed}/{m.ot_total} observations"),
    ]
    if m.ot_total:
        rows.append((
            "Observation shippability (prog.)",
            pct(ship_passed, m.ot_total),
            SHIPPABILITY_TARGET,
            f"{ship_passed}/{m.ot_total} observations",
        ))
    return rows


def format_table(rows: _RowList) -> str:
    lines = [
        f"{'Dimension':<40} {'Rate':>8} {'Target':>8} {'Floor':>8}  Result  Detail",
        "-" * 110,
    ]
    for name, rate, (target, floor), detail in rows:
        v = verdict(rate, target, floor)
        lines.append(
            f"{name:<40} {rate*100:>7.1f}% {target*100:>7.0f}% {floor*100:>7.0f}%"
            f"  {v:<6}  {detail}"
        )
    return "\n".join(lines)


def format_eg_failures(m: Metrics, max_n: int = 20) -> str:
    if not m.eg_failures:
        return ""
    lines = [f"Evidence grounding failures (first {max_n}):"]
    for key, ev in m.eg_failures[:max_n]:
        snippet = ev if len(ev) <= 100 else ev[:97] + "..."
        lines.append(f"  {key[:12]}  {snippet!r}")
    if len(m.eg_failures) > max_n:
        lines.append(f"  ...and {len(m.eg_failures) - max_n} more")
    return "\n".join(lines)


def report(m: Metrics, show_failures: bool) -> None:
    print()
    print(format_table(metrics_rows(m)))

    if show_failures:
        failures = format_eg_failures(m)
        if failures:
            print()
            print(failures)


def report_audit(am: AuditMetrics, show_failures: bool, m: Metrics | None = None) -> None:
    print()
    print(f"Reference-Free Audit (N={am.obs_total} observations, {am.signals_total} signals)")
    if am.signals_total == 0:
        print("  (no signals to audit)")
        return

    rows: _RowList = [
        ("Evidence grounded (judge)",
         pct(am.grounded_passed, am.signals_total),
         AUDIT_TARGET,
         f"{am.grounded_passed}/{am.signals_total} signals"),
        ("Reasoning justifies classification",
         pct(am.reasoning_passed, am.signals_total),
         AUDIT_TARGET,
         f"{am.reasoning_passed}/{am.signals_total} signals"),
        ("No over-extraction",
         pct(am.over_extraction_passed, am.signals_total),
         AUDIT_TARGET,
         f"{am.over_extraction_passed}/{am.signals_total} signals"),
    ]

    if m is not None:
        audited_obs = {s.cache_key for s in am.audited_signals}
        eg_failed_obs = {k for (k, _ev) in m.eg_failures}
        over_failed_obs = {e.cache_key for e in am.over_extraction_failures}
        total = len(audited_obs)
        if total:
            failed = len(audited_obs & (eg_failed_obs | over_failed_obs))
            passed = total - failed
            rows.append((
                "Observation shippability (full)",
                pct(passed, total),
                SHIPPABILITY_TARGET,
                f"{passed}/{total} observations",
            ))

    print(format_table(rows))

    if not show_failures:
        return

    def _dump(label: str, entries: list[AuditCheckResult]) -> None:
        if not entries:
            return
        print()
        print(f"{label} failures (first {min(10, len(entries))}):")
        for e in entries[:10]:
            note = e.note if len(e.note) <= 80 else e.note[:77] + "..."
            print(f"  {e.cache_key[:12]}  [sig {e.signal_index}]  {e.evidence_snippet!r}  → {note}")
        if len(entries) > 10:
            print(f"  ...and {len(entries) - 10} more")

    _dump("Evidence grounded", am.grounded_failures)
    _dump("Reasoning justifies classification", am.reasoning_failures)
    _dump("No over-extraction", am.over_extraction_failures)
