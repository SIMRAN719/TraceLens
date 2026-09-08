import numpy as np
from app.matcher import classify, cosine_similarity

def test_similarity():
    assert cosine_similarity(np.array([1, 0]), np.array([1, 0])) == 1.0
    assert abs(cosine_similarity(np.array([1, 0]), np.array([0, 1]))) < 1e-6

def test_classification():
    assert classify(0.49) == "NO_MATCH"
    assert classify(0.60) == "POSSIBLE_MATCH"
    assert classify(0.70) == "STRONG_MATCH"
