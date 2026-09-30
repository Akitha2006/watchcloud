from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserLoginSchema(BaseModel):
    username: str
    password: str

class UserRegisterSchema(BaseModel):
    username: str
    password: str
    confirm_password: Optional[str] = None

class SearchQuerySchema(BaseModel):
    query: str

class SimulationRequest(BaseModel):
    source_ip: Optional[str] = "192.168.1.100"
    username: Optional[str] = "user"
    payload: Optional[str] = ""
    request_count: Optional[int] = 60
    target_role: Optional[str] = "ADMIN"
    current_role: Optional[str] = "USER"

class IncidentSchema(BaseModel):
    incident_id: str
    type: str
    severity: str
    timestamp: str
    source: str
    description: str
    evidence: List[str] = []
    possible_cause: Optional[str] = ""
    status: str = "DETECTED"
    remediation: Optional[str] = ""
    verification: Optional[str] = ""
    report: Optional[str] = ""
