from remediation.executor import remediation_executor
from incidents.manager import incident_manager
from monitoring.log_monitor import log_event

class RemediationAgent:
    """
    Remediation Agent Responsibilities:
    - select safe remediation action
    - execute remediation action via RemediationExecutor
    - record remediation details in incident
    """
    def execute_remediation(self, incident: dict, metadata: dict = None) -> dict:
        action_details = remediation_executor.execute(
            incident["type"],
            incident["source"],
            metadata
        )

        incident_manager.update_incident(incident["incident_id"], {
            "remediation": action_details
        })

        log_event(
            "INFO",
            "REMEDIATION_EXECUTED",
            f"RemediationAgent executed action for {incident['incident_id']}: {action_details}",
            source="RemediationAgent"
        )

        return incident_manager.get_incident(incident["incident_id"])

remediation_agent = RemediationAgent()
