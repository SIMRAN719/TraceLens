# Technical notes

`FaceEngine` lazily initializes InsightFace `FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])` and prepares it with CPU context and a 640×640 detector input. It detects all faces, selects the largest bounding box, normalizes its embedding, and records the count and selected index.

`SerpApiLens` first uploads the local image to SerpApi's `/image` endpoint, obtains `image_id`, then calls the Google Lens engine with that identifier. Candidate fields are normalized defensively. Candidate downloads require an image content type and are bounded to 10 MiB; inaccessible and malformed candidates are skipped.

Matching uses cosine similarity. The 0.50 possible-match and 0.70 strong-match thresholds are configurable demo heuristics, not universal biometric thresholds. No embedding is persisted in the report or sent to the blockchain.

Evidence consists only of obtained post metadata and the downloaded image SHA-256. A canonical JSON serialization uses sorted keys, compact separators, UTF-8, and SHA-256 to produce a 32-byte/64-hex fingerprint. The Solidity registry stores fingerprint, block timestamp, and submitter, rejects duplicates, and exposes a read-only verification function.

Polygon Amoy uses chain ID 80002. Web3.py builds, signs, sends, and waits for a transaction using a locally loaded `.env` private key. The key is never written to reports. Verification is read-only. Recomputing a changed evidence object yields a different fingerprint and produces `TAMPER_DETECTED`.

Unit tests cover canonical hashing, similarity/classification, and verification with a mocked chain lookup. Face-model, SerpApi, and blockchain integration should be tested separately with authorized credentials and testnet funds.
