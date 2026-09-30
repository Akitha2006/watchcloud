import urllib.request
import json
from backend.config import LLM_API_KEY, LLM_MODEL

def analyze_root_cause_with_llm(incident_type: str, severity: str, evidence: list, rag_context: list) -> dict:
    """
    Analyzes incident root cause using LLM if LLM_API_KEY is configured,
    otherwise falls back to rule-based Demo Mode.
    """
    if not LLM_API_KEY:
        # Rule-based Demo Mode analysis
        demo_causes = {
            "DDOS_TRAFFIC": {
                "cause": "Abnormal request rate surge from simulated traffic source.",
                "reason": "Request volume exceeded safe configured threshold, indicating automated HTTP flood traffic."
            },
            "SQL_INJECTION": {
                "cause": "Malicious SQL syntax patterns detected in incoming request parameters.",
                "reason": "Unsanitized user payload contained database query keywords (e.g. UNION SELECT, OR 1=1)."
            },
            "BRUTE_FORCE": {
                "cause": "Repeated unauthorized authentication attempts against targeted user account.",
                "reason": "Multiple consecutive failed login attempts exceeded the security threshold."
            },
            "PRIVILEGE_ESCALATION": {
                "cause": "Unauthorized attempt to alter user permissions from normal_user to administrator.",
                "reason": "Request attempted an RBAC violation without valid security token or administrative consent."
            }
        }

        fallback = demo_causes.get(incident_type, {
            "cause": "Unusual application behavior detected.",
            "reason": "Automated security policy triggered."
        })

        return {
            "analysis_mode": "demo",
            "possible_cause": fallback["cause"],
            "reasoning": fallback["reason"],
            "rag_reference": rag_context[0]["incident_id"] if rag_context else "N/A"
        }

    # If LLM API Key is configured, attempt LLM API call
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
        prompt_content = f"Incident: {incident_type}, Severity: {severity}, Evidence: {evidence}, Historical KB: {rag_context}"
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are WatchCloud Root Cause AI Agent. Output JSON with fields 'possible_cause' and 'reasoning'."},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": 0.2
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            content = res_data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return {
                "analysis_mode": "llm",
                "possible_cause": parsed.get("possible_cause", "LLM Analysis Completed"),
                "reasoning": parsed.get("reasoning", content),
                "rag_reference": rag_context[0]["incident_id"] if rag_context else "N/A"
            }
    except Exception as e:
        return {
            "analysis_mode": "demo_fallback",
            "possible_cause": f"Rule-Based Analysis (LLM call failed/unavailable)",
            "reasoning": f"Incident pattern matches known signature for {incident_type}. (Error: {str(e)})",
            "rag_reference": rag_context[0]["incident_id"] if rag_context else "N/A"
        }
