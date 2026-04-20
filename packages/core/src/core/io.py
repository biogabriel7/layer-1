"""Generic JSONL read/write helpers used across layers.

Layer 1 appends extractions to jsonl; Layer 1.5 will read them. Keeping the
primitives here avoids duplicating jsonl handling in each layer.
"""

import json
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

_DEFAULT_LOCK = threading.Lock()


def append_jsonl(path: Path, record: dict[str, Any], lock: threading.Lock | None = None) -> None:
    """Append one JSON object as a single line, serialized under a lock so
    concurrent workers can't interleave bytes."""
    effective_lock = lock if lock is not None else _DEFAULT_LOCK
    line = json.dumps(record, ensure_ascii=False)
    with effective_lock, path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield each valid JSON object in a jsonl file.

    Tolerates a truncated trailing line from a prior crash (skips it).
    Non-dict records are skipped silently.
    """
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                yield rec
