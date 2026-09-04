"""Local evidence recomputation and on-chain comparison."""
from __future__ import annotations

from typing import Any, Callable

from .fingerprint import evidence_fingerprint, file_sha256


def verify_evidence(evidence: dict[str, Any], expected_fingerprint: str,
                    chain_lookup: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    recomputed = evidence_fingerprint(evidence)
    chain = chain_lookup(recomputed)
    matches = recomputed == expected_fingerprint and bool(chain.get("exists"))
    return {"recomputed_fingerprint": recomputed, "chain": chain, "blockchain_match": matches,
            "status": "VERIFIED" if matches else "TAMPER_DETECTED"}


def hash_image(path: str) -> str:
    return file_sha256(path)
