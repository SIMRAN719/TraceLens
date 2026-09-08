from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from app.face_engine import FaceEngine, FaceEngineError
from app.fingerprint import evidence_fingerprint, file_sha256
from app.matcher import classify, cosine_similarity
from app.reverse_search import ReverseSearchError, SerpApiLens
from app.candidate_fetcher import fetch_candidates


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="TraceLens: face -> web -> evidence -> blockchain")
    parser.add_argument("--image", required=True)
    parser.add_argument("--stage", choices=["face", "search", "match", "full"], default="full")
    parser.add_argument("--no-blockchain", action="store_true", help="Run analysis without registration")
    args = parser.parse_args()
    image = Path(args.image)
    if not image.is_file():
        parser.error(f"Image does not exist: {image}")
    try:
        engine = FaceEngine()
        reference = engine.analyze(image)
        print(f"Faces detected: {reference.faces_detected}; selected face: {reference.selected_face}")
        if args.stage == "face": return 0
        candidates = SerpApiLens().search(image)
        print(f"Google Lens candidates: {len(candidates)}")
        if args.stage == "search": return 0
        fetched = fetch_candidates(candidates, "data/candidates")
        ranked = []
        for candidate, path in fetched:
            try:
                result = engine.analyze(path)
                score = cosine_similarity(reference.embedding, result.embedding)
                ranked.append((score, candidate, path, result))
            except FaceEngineError:
                continue
        ranked.sort(key=lambda item: item[0], reverse=True)
        for score, candidate, _, _ in ranked:
            print(f"#{candidate.rank} {candidate.source or 'unknown'} {score:.3f} {classify(score)}")
        if args.stage == "match": return 0
        if not ranked:
            print("No verifiable face match found.")
            return 2
        score, candidate, path, _ = ranked[0]
        evidence = {"post_url": candidate.result_url, "source": candidate.source,
                    "title": candidate.title, "image_sha256": file_sha256(path)}
        fingerprint = evidence_fingerprint(evidence)
        report = {"project": "TraceLens", "query_image": str(image),
                  "face_analysis": {"faces_detected": reference.faces_detected, "embedding_generated": True},
                  "reverse_search": {"engine": "Google Lens", "results_found": len(candidates)},
                  "match": {"source": candidate.source, "url": candidate.result_url, "title": candidate.title,
                            "face_similarity": score, "classification": classify(score)},
                  "evidence": {**evidence, "fingerprint": fingerprint}}
        if not args.no_blockchain:
            from app.blockchain import ContentRegistryClient
            client = ContentRegistryClient()
            tx_hash = client.register(fingerprint)
            verification = client.verify(fingerprint)
            report["blockchain"] = {"network": "Polygon Amoy", "chain_id": 80002,
                                    "transaction_hash": tx_hash, "registered": verification["exists"]}
            report["verification"] = {"blockchain_match": verification["exists"],
                                       "status": "VERIFIED" if verification["exists"] else "TAMPER_DETECTED"}
        Path("data/results").mkdir(parents=True, exist_ok=True)
        Path("data/results/final_result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Evidence fingerprint: {fingerprint}\nReport: data/results/final_result.json")
        return 0
    except (FaceEngineError, ReverseSearchError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
