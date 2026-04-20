"""Name → student_id resolution over the roster.

At st-francis only 42% of students are unique by first name alone, so global
first-name matching is unreliable. Resolution tries these steps in order:
  1. full_name literal match
  2. unique first-name match within the crews of the tagged student_ids
  3. unique first-name match client-wide
  4. give up (ambiguous or unresolved) — caller may pass to the Attribution LLM
"""

import unicodedata
from collections.abc import Iterable

from layer_1_5.pipeline.models import ResolvedName, RosterStudent


def _normalize(s: str) -> str:
    """Unicode-NFC, lowercase, whitespace-collapsed, leading/trailing punctuation trimmed."""
    s = unicodedata.normalize("NFC", s).lower()
    s = " ".join(s.split())
    return s.strip(" \t\n\r\"'“”‘’.,;:!?")


class RosterIndex:
    """Indexed roster for constant-time name lookups, with crew-scoped views."""

    def __init__(self, roster: dict[str, RosterStudent]) -> None:
        self.roster = roster
        self._by_full: dict[str, list[str]] = {}
        self._by_first: dict[str, list[str]] = {}
        self._by_crew_first: dict[tuple[str, str], list[str]] = {}
        for sid, s in roster.items():
            full_n = _normalize(s.full_name)
            first_n = _normalize(s.first_name)
            if full_n:
                self._by_full.setdefault(full_n, []).append(sid)
            if first_n:
                self._by_first.setdefault(first_n, []).append(sid)
                self._by_crew_first.setdefault((s.crew_id, first_n), []).append(sid)

    def resolve(self, name: str, crew_ids: Iterable[str] = ()) -> ResolvedName:
        """Resolve a surface-form name. `crew_ids` is the set of crews attached
        to the observation's tagged student_ids — used to narrow ambiguous
        first-name matches."""
        n = _normalize(name)
        if not n:
            return ResolvedName(name_in_text=name, student_id=None, match_kind="unresolved")

        # 1. Exact full-name match (unique) → win.
        hits = self._by_full.get(n, [])
        if len(hits) == 1:
            return ResolvedName(
                name_in_text=name, student_id=hits[0], match_kind="full_name"
            )

        # 2. Unique first-name within one of the tagged crews.
        crew_ids_list = [c for c in crew_ids if c]
        if crew_ids_list:
            crew_hits: list[str] = []
            for cid in crew_ids_list:
                crew_hits.extend(self._by_crew_first.get((cid, n), []))
            crew_hits = list(dict.fromkeys(crew_hits))  # dedupe preserving order
            if len(crew_hits) == 1:
                return ResolvedName(
                    name_in_text=name,
                    student_id=crew_hits[0],
                    match_kind="first_name_unique_in_crew",
                )
            if len(crew_hits) > 1:
                return ResolvedName(
                    name_in_text=name,
                    student_id=None,
                    match_kind="ambiguous",
                    candidates=crew_hits,
                )

        # 3. Unique first-name client-wide.
        first_hits = self._by_first.get(n, [])
        if len(first_hits) == 1:
            return ResolvedName(
                name_in_text=name,
                student_id=first_hits[0],
                match_kind="first_name_unique_client",
            )
        if len(first_hits) > 1:
            return ResolvedName(
                name_in_text=name,
                student_id=None,
                match_kind="ambiguous",
                candidates=first_hits,
            )

        return ResolvedName(name_in_text=name, student_id=None, match_kind="unresolved")

    def crew_ids_for(self, student_ids: Iterable[str]) -> set[str]:
        """Return the set of crew_ids that the given students belong to."""
        crews: set[str] = set()
        for sid in student_ids:
            s = self.roster.get(sid)
            if s is not None and s.crew_id:
                crews.add(s.crew_id)
        return crews

    def get(self, student_id: str) -> RosterStudent | None:
        return self.roster.get(student_id)

    def __contains__(self, student_id: object) -> bool:
        return student_id in self.roster

    def __len__(self) -> int:
        return len(self.roster)
