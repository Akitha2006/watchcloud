from ai.rag_service import rag_service
from ai.llm_service import analyze_root_cause_with_llm
from monitoring.log_monitor import log_event
from incidents.manager import incident_manager

class RootCauseAgent:
    """
    Root Cause Agent Responsibilities:
    - analyze incident evidence
    - retrieve similar historical incidents from RAG knowledge base
    - determine likely cause using LLM / Demo Mode rule-based reasoning
    """
    def analyze(self, incident: dict) -> dict:
        incident_type = incident["type"]
        severity = incident["severity"]
        evidence = incident["evidence"]

        # 1. RAG Knowledge Retrieval
        rag_context = rag_service.retrieve_similar_incidents(incident_type)

        # 2. LLM / Demo Root Cause Analysis
        analysis_result = analyze_root_cause_with_llm(incident_type, severity, evidence, rag_context)

        possible_cause = f"[{analysis_result['analysis_mode'].upper()}] {analysis_result['possible_cause']} - {analysis_result['reasoning']}"

        # 3. Update Incident State
        incident_manager.update_incident(incident["incident_id"], {
            "possible_cause": possible_cause,
            "status": "IN_PROGRESS"
        })

        log_event(
            "INFO",
            "ROOT_CAUSE_ANALYSIS",
            f"RootCauseAgent analyzed {incident['incident_id']}: {possible_cause}",
            source="RootCauseAgent"
        )

        return incident_manager.get_incident(incident["incident_id"])

root_cause_agent = RootCauseAgent()
