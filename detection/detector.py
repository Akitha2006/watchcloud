from detection.traffic_detector import detect_traffic_anomaly
from detection.sql_detector import detect_sql_injection
from detection.brute_force_detector import detect_brute_force
from detection.privilege_detector import detect_privilege_escalation

class IncidentDetector:
    @staticmethod
    def check_traffic(request_count: int, source_ip: str = "192.168.1.100") -> dict:
        return detect_traffic_anomaly(request_count, source_ip)

    @staticmethod
    def check_sql(payload: str, source_ip: str = "192.168.1.101") -> dict:
        return detect_sql_injection(payload, source_ip)

    @staticmethod
    def check_brute_force(failed_count: int, username: str = "admin", source_ip: str = "192.168.1.102") -> dict:
        return detect_brute_force(failed_count, username, source_ip)

    @staticmethod
    def check_privilege(current_role: str, target_role: str, username: str = "user_1", source_ip: str = "192.168.1.103") -> dict:
        return detect_privilege_escalation(current_role, target_role, username, source_ip)

detector = IncidentDetector()
