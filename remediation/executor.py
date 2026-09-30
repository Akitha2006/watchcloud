from remediation.actions import (
    remediate_ddos,
    remediate_sql_injection,
    remediate_brute_force,
    remediate_privilege_escalation
)

class RemediationExecutor:
    @staticmethod
    def execute(incident_type: str, source: str, metadata: dict = None) -> str:
        if metadata is None:
            metadata = {}
            
        username = metadata.get("username", "admin_user")
        
        if incident_type == "DDOS_TRAFFIC":
            return remediate_ddos(source)
        elif incident_type == "SQL_INJECTION":
            return remediate_sql_injection(source)
        elif incident_type == "BRUTE_FORCE":
            return remediate_brute_force(username, source)
        elif incident_type == "PRIVILEGE_ESCALATION":
            return remediate_privilege_escalation(username)
        else:
            return f"Applied default security isolation policy for source {source}."

remediation_executor = RemediationExecutor()
