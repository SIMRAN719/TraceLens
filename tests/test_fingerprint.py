from app.fingerprint import canonical_json, evidence_fingerprint

def test_canonical_order_independent():
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})

def test_evidence_deterministic_and_sensitive():
    a = {"post_url": "x", "image_sha256": "a"}
    assert evidence_fingerprint(a) == evidence_fingerprint({"image_sha256": "a", "post_url": "x"})
    assert evidence_fingerprint(a) != evidence_fingerprint({"post_url": "y", "image_sha256": "a"})
