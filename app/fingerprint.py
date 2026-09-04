"""Streaming file and canonical evidence SHA-256 fingerprints."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def evidence_fingerprint(evidence: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(evidence).encode("utf-8")).hexdigest()
