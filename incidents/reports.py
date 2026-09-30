def generate_incident_report(incident: dict) -> str:
    """
    Generates a structured human-readable incident report.
    """
    evidence_str = "\n".join([f"  - {e}" for e in incident.get("evidence", [])]) or "  - None"

    report = f"""==========================================
WATCHCLOUD INCIDENT REPORT
==========================================
Incident ID:     {incident.get('incident_id')}
Incident Type:   {incident.get('type')}
Severity:        {incident.get('severity')}
Detected At:     {incident.get('timestamp')}
Source:          {incident.get('source')}

Description:
{incident.get('description')}

Evidence:
{evidence_str}

Possible Cause:
{incident.get('possible_cause', 'N/A')}

Remediation Action:
{incident.get('remediation', 'N/A')}

Verification Result:
{incident.get('verification', 'N/A')}

Final Status:    {incident.get('status')}
=========================================="""

    return report
