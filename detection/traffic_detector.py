from backend.config import DDOS_SUSPICIOUS_THRESHOLD, DDOS_CRITICAL_THRESHOLD

def detect_traffic_anomaly(request_count: int, source_ip: str) -> dict:
    """
    Evaluates HTTP request frequency for DDoS / abnormal traffic patterns.
    - Normal: < 20 requests
    - Suspicious: 20–50 requests
    - Critical: > 50 requests
    """
    if request_count > DDOS_CRITICAL_THRESHOLD:
        return {
            "detected": True,
            "type": "DDOS_TRAFFIC",
            "severity": "CRITICAL",
            "source": source_ip,
            "description": f"Abnormal high request volume ({request_count} req/sec) detected from source IP {source_ip}.",
            "evidence": [
                f"Request rate: {request_count} req/sec",
                f"Critical threshold: >{DDOS_CRITICAL_THRESHOLD} req/sec",
                f"Source IP: {source_ip}"
            ]
        }
    elif request_count >= DDOS_SUSPICIOUS_THRESHOLD:
        return {
            "detected": True,
            "type": "DDOS_TRAFFIC",
            "severity": "HIGH",
            "source": source_ip,
            "description": f"Suspicious traffic surge ({request_count} req/sec) detected from source IP {source_ip}.",
            "evidence": [
                f"Request rate: {request_count} req/sec",
                f"Suspicious threshold: >={DDOS_SUSPICIOUS_THRESHOLD} req/sec",
                f"Source IP: {source_ip}"
            ]
        }

    return {"detected": False}
