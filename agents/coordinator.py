from agents.detection_agent import detection_agent
from agents.root_cause_agent import root_cause_agent
from agents.remediation_agent import remediation_agent
from agents.verification_agent import verification_agent
from agents.reporting_agent import reporting_agent
from monitoring.log_monitor import log_event
from backend.state import system_state

class CoordinatorAgent:
    """
    Coordinator Agent Orchestrator:
    Manages the multi-agent autonomous self-healing pipeline:
    Detection -> Root Cause Analysis (RAG+LLM) -> Remediation -> Verification -> Reporting
    """
    def handle_incident_simulation(self, incident_category: str, simulation_data: dict) -> dict:
        log_event(
            "INFO",
            "COORDINATOR_START",
            f"CoordinatorAgent initiated workflow for category: {incident_category}",
            source="CoordinatorAgent"
        )

        # Step 1: Detection Agent
        incident = detection_agent.run_detection(incident_category, simulation_data)
        if not incident:
            return {"status": "NO_INCIDENT_DETECTED", "message": "Parameters did not breach detection thresholds."}

        inc_id = incident["incident_id"]
        system_state.add_agent_activity(inc_id, "Detection Agent", "COMPLETED", f"Identified {incident['type']} (Severity: {incident['severity']})")

        # Step 2: Root Cause Agent & RAG Service
        system_state.add_agent_activity(inc_id, "RAG Service", "IN_PROGRESS", "Retrieving historical signatures from knowledge base...")
        system_state.add_agent_activity(inc_id, "Root Cause Agent", "IN_PROGRESS", "Analyzing root cause & evidence...")
        
        incident = root_cause_agent.analyze(incident)
        
        system_state.add_agent_activity(inc_id, "RAG Service", "COMPLETED", "Historical KB patterns retrieved successfully.")
        system_state.add_agent_activity(inc_id, "Root Cause Agent", "COMPLETED", f"Root cause determined: {incident['possible_cause']}")

        # Step 3: Remediation Agent
        system_state.add_agent_activity(inc_id, "Remediation Agent", "IN_PROGRESS", "Executing safe application-level remediation...")
        incident = remediation_agent.execute_remediation(incident, simulation_data)
        system_state.add_agent_activity(inc_id, "Remediation Agent", "COMPLETED", f"Remediation executed: {incident['remediation']}")

        # Step 4: Verification Agent
        system_state.add_agent_activity(inc_id, "Verification Agent", "IN_PROGRESS", "Verifying system recovery & condition reset...")
        incident = verification_agent.verify(incident, simulation_data)
        system_state.add_agent_activity(inc_id, "Verification Agent", "COMPLETED", f"Recovery status: {incident['status']}")

        # Step 5: Reporting Agent
        system_state.add_agent_activity(inc_id, "Reporting Agent", "IN_PROGRESS", "Compiling incident report...")
        incident = reporting_agent.generate_report(incident)
        system_state.add_agent_activity(inc_id, "Reporting Agent", "COMPLETED", "Final incident report generated.")

        log_event(
            "INFO",
            "COORDINATOR_COMPLETE",
            f"CoordinatorAgent completed self-healing lifecycle for {incident['incident_id']} (Final Status: {incident['status']})",
            source="CoordinatorAgent"
        )

        return incident

coordinator_agent = CoordinatorAgent()
