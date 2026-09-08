"""Safe, bounded downloads of candidate images."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from .reverse_search import SearchCandidate


def fetch_candidates(candidates: list[SearchCandidate], output_dir: str | Path,
                     max_bytes: int = 10 * 1024 * 1024, timeout: int = 20) -> list[tuple[SearchCandidate, Path]]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    found: list[tuple[SearchCandidate, Path]] = []
    for index, candidate in enumerate(candidates, 1):
        if not candidate.image_url:
            continue
        try:
            response = requests.get(candidate.image_url, stream=True, timeout=timeout,
                                    headers={"User-Agent": "TraceLens/1.0 authorized-demo"})
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                continue
            length = int(response.headers.get("content-length") or 0)
            if length > max_bytes:
                continue
            path = directory / f"candidate_{index:03d}.img"
            total = 0
            with path.open("wb") as handle:
                for chunk in response.iter_content(64 * 1024):
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError("image exceeds maximum size")
                    handle.write(chunk)
            found.append((candidate, path))
        except (requests.RequestException, OSError, ValueError):
            continue
    return found
