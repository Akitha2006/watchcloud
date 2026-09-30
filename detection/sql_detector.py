from backend.config import SQL_INJECTION_PATTERNS

def detect_sql_injection(input_payload: str, source_ip: str) -> dict:
    """
    Scans input parameters for SQL Injection keywords without executing the payload.
    """
    if not input_payload:
        return {"detected": False}

    upper_payload = input_payload.upper()
    found_patterns = []

    for pattern in SQL_INJECTION_PATTERNS:
        if pattern.upper() in upper_payload:
            found_patterns.append(pattern)

    if found_patterns:
        return {
            "detected": True,
            "type": "SQL_INJECTION",
            "severity": "HIGH",
            "source": source_ip,
            "description": f"Potential SQL Injection attempt detected in input payload from {source_ip}.",
            "evidence": [
                f"Matched malicious patterns: {', '.join(found_patterns)}",
                f"Raw input payload: '{input_payload}'",
                f"Source IP: {source_ip}"
            ]
        }

    return {"detected": False}
