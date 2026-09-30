from backend.state import system_state
from monitoring.log_monitor import log_event
from backend.database import get_db_connection

def remediate_ddos(source_ip: str) -> str:
    system_state.blocked_ips.add(source_ip)
    system_state.rate_limit_active = True
    system_state.traffic_window_count = 0
    action_msg = f"Applied application rate-limiting rule and added {source_ip} to temporary blocked list."
    log_event("INFO", "REMEDIATION_ACTION", action_msg, source="RemediationEngine")
    return action_msg

def remediate_sql_injection(source_ip: str) -> str:
    system_state.blocked_ips.add(source_ip)
    action_msg = f"Rejected malicious payload and added source {source_ip} to application security filter blocklist."
    log_event("INFO", "REMEDIATION_ACTION", action_msg, source="RemediationEngine")
    return action_msg

def remediate_brute_force(username: str, source_ip: str) -> str:
    system_state.locked_accounts.add(username)
    system_state.failed_login_counters[username] = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_locked = 1 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error locking user in DB: {e}")

    action_msg = f"Temporarily locked account '{username}' and reset failed authentication attempt counter."
    log_event("INFO", "REMEDIATION_ACTION", action_msg, source="RemediationEngine")
    return action_msg

def remediate_privilege_escalation(username: str) -> str:
    system_state.user_roles[username] = "USER"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = 'USER' WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error resetting role in DB: {e}")

    action_msg = f"Denied elevated permissions for account '{username}' and restored role to 'USER'."
    log_event("INFO", "REMEDIATION_ACTION", action_msg, source="RemediationEngine")
    return action_msg
