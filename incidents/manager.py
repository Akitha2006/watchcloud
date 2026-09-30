from backend.state import system_state
from backend.utils import get_timestamp

class IncidentManager:
    @staticmethod
    def create_incident(detection_data: dict) -> dict:
        incident_id = system_state.generate_incident_id()
        incident = {
            "incident_id": incident_id,
            "type": detection_data.get("type", "UNKNOWN"),
            "severity": detection_data.get("severity", "MEDIUM"),
            "timestamp": get_timestamp(),
            "source": detection_data.get("source", "127.0.0.1"),
            "description": detection_data.get("description", "Security incident detected"),
            "evidence": detection_data.get("evidence", []),
            "possible_cause": "",
            "status": "DETECTED",
            "remediation": "",
            "verification": "",
            "report": ""
        }
        system_state.add_incident(incident)
        return incident

    @staticmethod
    def update_incident(incident_id: str, updates: dict) -> dict:
        system_state.update_incident(incident_id, updates)
        return system_state.get_incident(incident_id)

    @staticmethod
    def get_all_incidents() -> list:
        return system_state.incidents

    @staticmethod
    def get_incident(incident_id: str) -> dict:
        return system_state.get_incident(incident_id)

incident_manager = IncidentManager()
