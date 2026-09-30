from detection.detector import detector
from incidents.manager import incident_manager
from monitoring.log_monitor import log_event

class DetectionAgent:
    """
    Detection Agent Responsibilities:
    - analyze monitoring data & logs
    - identify incident type
    - assign severity
    - collect evidence & create incident
    """
    def run_detection(self, incident_category: str, simulation_data: dict) -> dict:
        source_ip = simulation_data.get("source_ip", "192.168.1.100")
        username = simulation_data.get("username", "admin_user")
        payload = simulation_data.get("payload", "")
        req_count = simulation_data.get("request_count", 60)
        current_role = simulation_data.get("current_role", "normal_user")
        target_role = simulation_data.get("target_role", "admin")

        detection_result = {"detected": False}

        if incident_category == "ddos":
            detection_result = detector.check_traffic(req_count, source_ip)
        elif incident_category == "sql":
            detection_result = detector.check_sql(payload, source_ip)
        elif incident_category == "brute_force":
            failed_count = simulation_data.get("failed_count", 5)
            detection_result = detector.check_brute_force(failed_count, username, source_ip)
        elif incident_category == "privilege":
            detection_result = detector.check_privilege(current_role, target_role, username, source_ip)

        if detection_result.get("detected"):
            incident = incident_manager.create_incident(detection_result)
            log_event(
                "WARNING",
                "INCIDENT_DETECTED",
                f"DetectionAgent identified {incident['type']} (Severity: {incident['severity']}) - ID: {incident['incident_id']}",
                source="DetectionAgent"
            )
            return incident
        
        return None

detection_agent = DetectionAgent()
