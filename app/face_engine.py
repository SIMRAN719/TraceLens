"""CPU InsightFace wrapper. Models are loaded lazily on first use."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class FaceEngineError(RuntimeError):
    """Raised when an image cannot be analyzed."""


@dataclass
class FaceAnalysisResult:
    embedding: np.ndarray
    faces_detected: int
    selected_face: int
    bbox: list[float]


class FaceEngine:
    def __init__(self, model_name: str = "buffalo_l") -> None:
        self.model_name = model_name
        self._app: Any | None = None

    def _load(self) -> Any:
        if self._app is None:
            try:
                from insightface.app import FaceAnalysis
            except ImportError as exc:
                raise FaceEngineError("InsightFace/ONNX Runtime is not installed.") from exc
            self._app = FaceAnalysis(name=self.model_name, providers=["CPUExecutionProvider"])
            self._app.prepare(ctx_id=-1, det_size=(640, 640))
        return self._app

    def analyze(self, image_path: str | Path) -> FaceAnalysisResult:
        path = Path(image_path)
        if not path.is_file():
            raise FaceEngineError(f"Image does not exist: {path}")
        image = cv2.imread(str(path))
        if image is None:
            raise FaceEngineError(f"Could not read image: {path}")
        faces = self._load().get(image)
        if not faces:
            raise FaceEngineError(f"No faces detected in {path}")
        # Largest bounding-box area is deterministic and documented policy.
        selected = max(range(len(faces)), key=lambda i: self._area(faces[i].bbox))
        face = faces[selected]
        embedding = np.asarray(face.embedding, dtype=np.float32)
        norm = float(np.linalg.norm(embedding))
        if norm == 0:
            raise FaceEngineError("InsightFace returned a zero-length embedding.")
        return FaceAnalysisResult(embedding=embedding / norm, faces_detected=len(faces),
                                  selected_face=selected, bbox=[float(x) for x in face.bbox])

    @staticmethod
    def _area(bbox: Any) -> float:
        return max(0.0, float(bbox[2] - bbox[0])) * max(0.0, float(bbox[3] - bbox[1]))
