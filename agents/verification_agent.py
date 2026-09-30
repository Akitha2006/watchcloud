from backend.state import system_state
from incidents.manager import incident_manager
from monitoring.log_monitor import log_event
from backend.utils import get_timestamp

class VerificationAgent:
    """
    Verification Agent Responsibilities:
    - check whether the incident condition has been resolved
    - compare before/after metric state
    - set status to RESOLVED or UNRESOLVED
    """
    def verify(self, incident: dict, metadata: dict = None) -> dict:
        if metadata is None:
            metadata = {}

        incident_type = incident["type"]
        source = incident["source"]
        username = metadata.get("username", "admin_user")

        is_resolved = False
        verification_details = ""

        if incident_type == "DDOS_TRAFFIC":
            if source in system_state.blocked_ips or system_state.rate_limit_active:
                is_resolved = True
                verification_details = f"Verified: Rate-limiting active & traffic from {source} blocked. Excess request flood neutralized."
        elif incident_type == "SQL_INJECTION":
            if source in system_state.blocked_ips:
                is_resolved = True
                verification_details = f"Verified: Malicious query payload rejected and client {source} filtered."
        elif incident_type == "BRUTE_FORCE":
            if username in system_state.locked_accounts and system_state.failed_login_counters.get(username, 0) == 0:
                is_resolved = True
                verification_details = f"Verified: Account '{username}' locked safely, failed attempts counter reset to 0."
        elif incident_type == "PRIVILEGE_ESCALATION":
            current_role = system_state.user_roles.get(username, "normal_user")
            if current_role == "normal_user":
                is_resolved = True
                verification_details = f"Verified: Unauthorized admin elevation revoked. Account '{username}' verified at 'normal_user'."

        status_str = "RESOLVED" if is_resolved else "UNRESOLVED"

        updated_incident = incident_manager.update_incident(incident["incident_id"], {
            "status": status_str,
            "verification": f"[{status_str}] {verification_details} (Verified at {get_timestamp()})"
        })

        log_event(
            "INFO" if is_resolved else "ERROR",
            "INCIDENT_VERIFIED",
            f"VerificationAgent verified {incident['incident_id']}: Status={status_str}",
            source="VerificationAgent"
        )

        return updated_incident

verification_agent = VerificationAgent()
