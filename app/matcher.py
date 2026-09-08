"""Embedding comparison and demo threshold classification."""
from __future__ import annotations

import numpy as np


def cosine_similarity(first: np.ndarray, second: np.ndarray) -> float:
    a, b = np.asarray(first, dtype=np.float32), np.asarray(second, dtype=np.float32)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0:
        raise ValueError("Cannot compare a zero-length embedding.")
    return float(np.dot(a, b) / denominator)


def classify(score: float, possible_threshold: float = 0.50, strong_threshold: float = 0.70) -> str:
    if score < possible_threshold:
        return "NO_MATCH"
    if score < strong_threshold:
        return "POSSIBLE_MATCH"
    return "STRONG_MATCH"
