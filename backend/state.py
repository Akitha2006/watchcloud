import json
import sqlite3
from typing import List, Dict, Any
from backend.utils import load_json_file, save_json_file, get_timestamp
from backend.config import INCIDENTS_FILE, LOGS_FILE
from backend.database import get_db_connection

class SystemState:
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = load_json_file(LOGS_FILE, [])
        self.incidents: List[Dict[str, Any]] = load_json_file(INCIDENTS_FILE, [])
        self.agent_activities: List[Dict[str, Any]] = []
        self.blocked_ips: set = set()
        self.locked_accounts: set = set()
        self.rate_limit_active: bool = False
        self.failed_login_counters: Dict[str, int] = {}
        self.user_roles: Dict[str, str] = {"user": "USER"}
        self.traffic_window_count: int = 0
        self.incident_counter: int = len(self.incidents)
        self.sync_from_db()

    def generate_incident_id(self) -> str:
        self.incident_counter += 1
        return f"INC-{self.incident_counter:04d}"

    def sync_from_db(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM incidents ORDER BY id DESC")
            db_incidents = cursor.fetchall()
            if db_incidents:
                self.incidents = []
                for row in db_incidents:
                    evidence = json.loads(row["evidence"]) if row["evidence"] else []
                    self.incidents.append({
                        "incident_id": row["incident_id"],
                        "type": row["type"],
                        "severity": row["severity"],
                        "timestamp": row["timestamp"],
                        "source": row["source"],
                        "description": row["description"],
                        "evidence": evidence,
                        "possible_cause": row["possible_cause"] or "",
                        "remediation": row["remediation"] or "",
                        "verification": row["verification"] or "",
                        "status": row["status"],
                        "report": row["report"] or ""
                    })
                self.incident_counter = len(self.incidents)
            conn.close()
        except Exception as e:
            print(f"Error syncing from DB: {e}")

    def add_log(self, log_entry: dict):
        self.logs.insert(0, log_entry)
        if len(self.logs) > 200:
            self.logs = self.logs[:200]
        save_json_file(LOGS_FILE, self.logs[:50])

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (timestamp, level, event, message, source, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (log_entry["timestamp"], log_entry["level"], log_entry["event"], log_entry["message"], log_entry["source"], json.dumps(log_entry.get("metadata", {})))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving log to DB: {e}")

    def add_agent_activity(self, incident_id: str, agent: str, status_val: str, message: str):
        activity = {
            "incident_id": incident_id,
            "agent": agent,
            "status": status_val,
            "message": message,
            "timestamp": get_timestamp()
        }
        self.agent_activities.insert(0, activity)
        if len(self.agent_activities) > 100:
            self.agent_activities = self.agent_activities[:100]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agent_activities (incident_id, agent, status, message, timestamp) VALUES (?, ?, ?, ?, ?)",
                (incident_id, agent, status_val, message, activity["timestamp"])
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving agent activity to DB: {e}")

    def add_incident(self, incident: dict):
        self.incidents.insert(0, incident)
        save_json_file(INCIDENTS_FILE, self.incidents)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO incidents 
                (incident_id, type, severity, timestamp, source, description, evidence, possible_cause, remediation, verification, status, report) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    incident["incident_id"],
                    incident["type"],
                    incident["severity"],
                    incident["timestamp"],
                    incident["source"],
                    incident["description"],
                    json.dumps(incident.get("evidence", [])),
                    incident.get("possible_cause", ""),
                    incident.get("remediation", ""),
                    incident.get("verification", ""),
                    incident.get("status", "DETECTED"),
                    incident.get("report", "")
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error inserting incident to DB: {e}")

    def update_incident(self, incident_id: str, updates: dict):
        for inc in self.incidents:
            if inc["incident_id"] == incident_id:
                inc.update(updates)
                break
        save_json_file(INCIDENTS_FILE, self.incidents)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query_parts = []
            params = []
            for k, v in updates.items():
                if k == "evidence":
                    v = json.dumps(v)
                query_parts.append(f"{k} = ?")
                params.append(v)
            params.append(incident_id)

            sql = f"UPDATE incidents SET {', '.join(query_parts)} WHERE incident_id = ?"
            cursor.execute(sql, tuple(params))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating incident in DB: {e}")

    def get_incident(self, incident_id: str) -> dict:
        for inc in self.incidents:
            if inc["incident_id"] == incident_id:
                return inc
        return None

system_state = SystemState()
