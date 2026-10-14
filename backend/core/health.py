def calculate_health_score(findings):
    score = 100

    severity_points = {
        "critical": 30,
        "high": 15,
        "warning": 5,
        "info": 0,
    }

    for finding in findings:
        severity = finding.get("severity", "").lower()
        score -= severity_points.get(severity, 0)

    score = max(score, 0)

    if score >= 90:
        status = "Excellent"
    elif score >= 75:
        status = "Good"
    elif score >= 50:
        status = "Needs attention"
    else:
        status = "Critical"

    return {
        "score": score,
        "status": status
    }
