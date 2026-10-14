
from core.health import calculate_health_score


def test_empty_findings_returns_perfect_score():
    result = calculate_health_score([])

    assert result == {
        "score": 100,
        "status": "Excellent",
    }


def test_critical_finding_reduces_score_by_30():
    result = calculate_health_score([
        {"severity": "critical"}
    ])

    assert result["score"] == 70
    assert result["status"] == "Needs attention"


def test_high_finding_reduces_score_by_15():
    result = calculate_health_score([
        {"severity": "high"}
    ])

    assert result["score"] == 85
    assert result["status"] == "Good"


def test_warning_finding_reduces_score_by_5():
    result = calculate_health_score([
        {"severity": "warning"}
    ])

    assert result["score"] == 95
    assert result["status"] == "Excellent"


def test_info_finding_does_not_reduce_score():
    result = calculate_health_score([
        {"severity": "info"}
    ])

    assert result["score"] == 100


def test_score_never_falls_below_zero():
    result = calculate_health_score([
        {"severity": "critical"}
        for _ in range(10)
    ])

    assert result["score"] == 0
    assert result["status"] == "Critical"


def test_severity_matching_is_case_insensitive():
    result = calculate_health_score([
        {"severity": "CRITICAL"}
    ])

    assert result["score"] == 70


def test_unknown_severity_does_not_crash():
    result = calculate_health_score([
        {"severity": "unexpected"}
    ])

    assert result["score"] == 100


def test_missing_severity_does_not_crash():
    result = calculate_health_score([
        {"category": "routing"}
    ])

    assert result["score"] == 100

