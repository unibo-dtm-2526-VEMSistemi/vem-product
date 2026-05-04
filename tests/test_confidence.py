import pytest
from src.confidence import compute_confidence


def test_perfect_match():
    result = compute_confidence(
        llm_confidence=100, cosine_distance=0.0, all_distances=[0.0, 0.5, 1.0]
    )
    assert result == 1.0


def test_worst_match():
    result = compute_confidence(
        llm_confidence=0, cosine_distance=2.0, all_distances=[0.0, 1.0, 2.0]
    )
    assert result == 0.0


def test_mid_range():
    result = compute_confidence(
        llm_confidence=50, cosine_distance=1.0, all_distances=[0.0, 1.0, 2.0]
    )
    assert result == 0.5


def test_all_distances_equal():
    result = compute_confidence(
        llm_confidence=80, cosine_distance=0.3, all_distances=[0.3, 0.3, 0.3]
    )
    assert result == 0.65  # 0.5*0.5 + 0.5*0.8


def test_result_is_rounded_to_4_decimals():
    result = compute_confidence(
        llm_confidence=73, cosine_distance=0.3, all_distances=[0.1, 0.3, 0.8]
    )
    assert result == 0.7221  # raw value is 0.722142857..., must be rounded


def test_penalty_for_hallucinated_code():
    result = compute_confidence(
        llm_confidence=60, cosine_distance=1.8, all_distances=[0.2, 0.5, 1.0, 1.8]
    )
    assert result == 0.3


def test_empty_distances_raises():
    with pytest.raises(ValueError, match="at least one element"):
        compute_confidence(llm_confidence=80, cosine_distance=0.5, all_distances=[])
