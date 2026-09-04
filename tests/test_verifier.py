from app.verifier import verify_evidence
from app.fingerprint import evidence_fingerprint

def test_verified():
    evidence = {"post_url": "x"}
    fp = evidence_fingerprint(evidence)
    result = verify_evidence(evidence, fp, lambda _: {"exists": True, "timestamp": 1, "submitter": "0x0"})
    assert result["status"] == "VERIFIED"

def test_tamper_detected():
    evidence = {"post_url": "x"}
    result = verify_evidence(evidence, "0" * 64, lambda _: {"exists": True})
    assert result["status"] == "TAMPER_DETECTED"
