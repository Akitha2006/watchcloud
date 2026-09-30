from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class LogEntry(BaseModel):
    timestamp: str
    level: str
    event: str
    message: str
    source: str
    metadata: Optional[Dict[str, Any]] = {}

class MetricEntry(BaseModel):
    timestamp: str
    cpu: float
    memory: float
    disk: float
    network_sent: int
    network_received: int

class Incident(BaseModel):
    incident_id: str
    type: str  # DDOS_TRAFFIC, SQL_INJECTION, BRUTE_FORCE, PRIVILEGE_ESCALATION
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    timestamp: str
    source: str
    description: str
    evidence: List[str] = []
    possible_cause: Optional[str] = ""
    status: str = "DETECTED"  # DETECTED, IN_PROGRESS, RESOLVED, UNRESOLVED
    remediation: Optional[str] = ""
    verification: Optional[str] = ""
    report: Optional[str] = ""

class SimulationRequest(BaseModel):
    source_ip: Optional[str] = "192.168.1.100"
    username: Optional[str] = "admin_user"
    payload: Optional[str] = ""
    request_count: Optional[int] = 60
    target_role: Optional[str] = "admin"
    current_role: Optional[str] = "normal_user"
