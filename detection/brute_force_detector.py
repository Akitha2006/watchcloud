from backend.config import BRUTE_FORCE_INCIDENT_LIMIT, BRUTE_FORCE_WARNING_LIMIT

def detect_brute_force(failed_count: int, username: str, source_ip: str) -> dict:
    """
    Evaluates failed login attempts for brute force authentication activity.
    - 3 failures: Warning
    - 5 failures: Incident
    """
    if failed_count >= BRUTE_FORCE_INCIDENT_LIMIT:
        return {
            "detected": True,
            "type": "BRUTE_FORCE",
            "severity": "HIGH",
            "source": source_ip,
            "description": f"Brute force login attack detected against user account '{username}' from IP {source_ip}.",
            "evidence": [
                f"Consecutive failed attempts: {failed_count}",
                f"Incident threshold: {BRUTE_FORCE_INCIDENT_LIMIT}",
                f"Target user: '{username}'",
                f"Source IP: {source_ip}"
            ]
        }
    elif failed_count >= BRUTE_FORCE_WARNING_LIMIT:
        return {
            "detected": True,
            "type": "BRUTE_FORCE",
            "severity": "MEDIUM",
            "source": source_ip,
            "description": f"Multiple authentication failures observed for user '{username}'.",
            "evidence": [
                f"Consecutive failed attempts: {failed_count}",
                f"Warning threshold: {BRUTE_FORCE_WARNING_LIMIT}",
                f"Target user: '{username}'"
            ]
        }

    return {"detected": False}
