def detect_privilege_escalation(current_role: str, target_role: str, username: str, source_ip: str) -> dict:
    """
    Detects unauthorized role changes (e.g. normal_user -> admin).
    """
    if current_role.lower() == "normal_user" and target_role.lower() == "admin":
        return {
            "detected": True,
            "type": "PRIVILEGE_ESCALATION",
            "severity": "CRITICAL",
            "source": source_ip,
            "description": f"Unauthorized privilege escalation attempt detected for account '{username}'.",
            "evidence": [
                f"Unauthorized role change: {current_role} -> {target_role}",
                f"Target Account: '{username}'",
                f"Authorization status: REJECTED",
                f"Source IP: {source_ip}"
            ]
        }

    return {"detected": False}
