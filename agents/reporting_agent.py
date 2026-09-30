from incidents.reports import generate_incident_report
from incidents.manager import incident_manager
from monitoring.log_monitor import log_event

class ReportingAgent:
    """
    Reporting Agent Responsibilities:
    - create human-readable incident report
    - include incident details, evidence, root cause, remediation, verification result
    """
    def generate_report(self, incident: dict) -> dict:
        report_text = generate_incident_report(incident)

        updated_incident = incident_manager.update_incident(incident["incident_id"], {
            "report": report_text
        })

        log_event(
            "INFO",
            "REPORT_GENERATED",
            f"ReportingAgent generated final incident report for {incident['incident_id']}",
            source="ReportingAgent"
        )

        return updated_incident

reporting_agent = ReportingAgent()
