ROOT_CAUSE_PROMPT = """
You are the WatchCloud Root Cause Analysis AI Agent.
Analyze the following incident:
Incident Type: {incident_type}
Severity: {severity}
Evidence: {evidence}
Description: {description}

Historical RAG Context:
{rag_context}

Provide a concise, professional analysis of the probable root cause and reasoning.
"""

REMEDIATION_PROMPT = """
You are the WatchCloud Remediation Agent.
Select the safest application-level remediation action for incident type: {incident_type}.
Target Source: {source}
"""
