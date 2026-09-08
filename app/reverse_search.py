"""SerpApi Google Lens upload and search client."""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests


class ReverseSearchError(RuntimeError):
    pass


@dataclass
class SearchCandidate:
    rank: int
    title: str
    source: str
    result_url: str
    image_url: str
    raw: dict[str, Any]


class SerpApiLens:
    def __init__(self, api_key: str | None = None, timeout: int = 45) -> None:
        self.api_key = api_key or os.getenv("SERPAPI_KEY", "").strip()
        self.timeout = timeout
        if not self.api_key:
            raise ReverseSearchError("SERPAPI_KEY is not configured.")

    def search(self, image_path: str | Path) -> list[SearchCandidate]:
        path = Path(image_path)
        if not path.is_file():
            raise ReverseSearchError(f"Search image does not exist: {path}")
        try:
            with path.open("rb") as handle:
                upload = requests.post("https://serpapi.com/image", files={"image": handle},
                                       data={"api_key": self.api_key}, timeout=self.timeout)
            upload.raise_for_status()
            payload = upload.json()
            image_id = payload.get("image_id")
            if not image_id:
                raise ReverseSearchError(f"SerpApi upload did not return image_id: {payload}")
            response = requests.get("https://serpapi.com/search", params={
                "engine": "google_lens", "image_id": image_id, "api_key": self.api_key
            }, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise ReverseSearchError(f"SerpApi request failed: {exc}") from exc
        except ValueError as exc:
            raise ReverseSearchError("SerpApi returned invalid JSON.") from exc
        candidates: list[SearchCandidate] = []
        for index, item in enumerate(data.get("visual_matches") or [], start=1):
            if not isinstance(item, dict):
                continue
            candidates.append(SearchCandidate(
                rank=int(item.get("position") or index), title=str(item.get("title") or ""),
                source=str(item.get("source") or ""), result_url=str(item.get("link") or ""),
                image_url=str(item.get("image") or item.get("thumbnail") or ""), raw=item))
        return candidates

    @staticmethod
    def serializable(candidates: list[SearchCandidate]) -> list[dict[str, Any]]:
        return [asdict(candidate) for candidate in candidates]
