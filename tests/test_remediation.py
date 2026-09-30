from remediation.actions import (
    remediate_ddos,
    remediate_sql_injection,
    remediate_brute_force,
    remediate_privilege_escalation
)
from backend.state import system_state

def test_remediate_ddos():
    msg = remediate_ddos("192.168.1.100")
    assert "192.168.1.100" in system_state.blocked_ips
    assert system_state.rate_limit_active is True

def test_remediate_sql():
    msg = remediate_sql_injection("192.168.1.101")
    assert "192.168.1.101" in system_state.blocked_ips

def test_remediate_brute_force():
    msg = remediate_brute_force("user", "192.168.1.102")
    assert "user" in system_state.locked_accounts
    assert system_state.failed_login_counters.get("user") == 0

def test_remediate_privilege():
    msg = remediate_privilege_escalation("user")
    assert "restored role to 'normal_user'" in msg.lower() or "denied" in msg.lower()
