from fastapi import APIRouter, HTTPException, Request, Response, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from monitoring.metrics import collect_metrics
from backend.state import system_state
from backend.models import SimulationRequest
from backend.schemas import UserLoginSchema, UserRegisterSchema, SearchQuerySchema
from backend.auth import (
    authenticate_user,
    register_new_user,
    create_session,
    destroy_session,
    get_current_user_from_request
)
from backend.database import get_db_connection
from agents.coordinator import coordinator_agent
from incidents.manager import incident_manager
from monitoring.log_monitor import log_event
from detection.detector import detector
from backend.config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ---------------- APPLICATION HOME & HEALTH ----------------
@router.get("/")
def home():
    return {
        "service": "WatchCloud Application & Self-Healing Platform",
        "status": "Running",
        "message": "Welcome to WatchCloud Autonomous Cloud Infrastructure",
        "links": {
            "login": "/login",
            "register": "/register",
            "user_dashboard": "/user/dashboard",
            "admin_dashboard": "/admin/dashboard",
            "watchcloud_dashboard": "/dashboard",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

@router.get("/health")
def health():
    return {
        "service": "WatchCloud Cloud Application",
        "status": "healthy"
    }

@router.get("/metrics")
def metrics():
    return collect_metrics()

# ---------------- AUTHENTICATION ROUTES ----------------
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = None, message: str = None):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": error, "message": message}
    )

@router.post("/login")
def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    source_ip = request.client.host if request.client else "127.0.0.1"
    user, reason = authenticate_user(username, password)

    if not user:
        # Track failed login attempt for Brute Force Detection
        current_failed = system_state.failed_login_counters.get(username, 0) + 1
        system_state.failed_login_counters[username] = current_failed

        log_event(
            "WARNING",
            "FAILED_LOGIN_ATTEMPT",
            f"Failed login attempt for user '{username}' (Failed count: {current_failed}) from {source_ip}",
            source="AuthService",
            metadata={"username": username, "failed_count": current_failed}
        )

        # Evaluate Brute Force threshold (5 failures)
        if current_failed >= 5:
            sim_data = {
                "source_ip": source_ip,
                "username": username,
                "failed_count": current_failed
            }
            coordinator_agent.handle_incident_simulation("brute_force", sim_data)

        err_msg = "Invalid username or password."
        if reason == "account_locked":
            err_msg = f"Account '{username}' is temporarily locked by WatchCloud due to brute force security policy."

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": err_msg},
            status_code=400
        )

    # Successful Login: reset failure counter
    system_state.failed_login_counters[username] = 0
    session_id = create_session(user["username"], user["role"])

    log_event("INFO", "USER_LOGIN_SUCCESS", f"User '{username}' (Role: {user['role']}) logged in successfully.", source="AuthService")

    redirect_url = "/admin/dashboard" if user["role"] == "ADMIN" else "/user/dashboard"
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, error: str = None):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": error}
    )

@router.post("/register")
def register_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Passwords do not match."},
            status_code=400
        )

    success, msg = register_new_user(username, password)
    if not success:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": msg},
            status_code=400
        )

    log_event("INFO", "USER_REGISTERED", f"New user '{username}' registered with USER role.", source="AuthService")

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": "Registration successful! Please log in."}
    )

@router.get("/logout")
def logout_action(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        destroy_session(session_id)
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response

# ---------------- USER & ADMIN DASHBOARDS ----------------
@router.get("/user/dashboard", response_class=HTMLResponse)
def user_dashboard(request: Request, alert_msg: str = None):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="user_dashboard.html",
        context={
            "username": str(user["username"]),
            "alert_msg": alert_msg
        }
    )

@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # ROLE-BASED AUTHORIZATION CHECK (PRIVILEGE ESCALATION DEMO TRIGGER)
    if user["role"] != "ADMIN":
        source_ip = request.client.host if request.client else "192.168.1.100"
        log_event(
            "WARNING",
            "UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT",
            f"User '{user['username']}' (Role: USER) attempted unauthorized access to ADMIN_PANEL",
            source="AuthorizationService",
            metadata={"user": user['username'], "requested_resource": "ADMIN_PANEL"}
        )

        # Trigger WatchCloud Privilege Escalation Incident Workflow
        sim_data = {
            "source_ip": source_ip,
            "username": user["username"],
            "current_role": "USER",
            "target_role": "ADMIN"
        }
        coordinator_agent.handle_incident_simulation("privilege", sim_data)

        # Redirect back to user dashboard with alert
        return RedirectResponse(
            url="/user/dashboard?alert_msg=Access+Denied!+Your+attempt+to+access+the+Admin+Panel+was+rejected.+WatchCloud+detected+a+Privilege+Escalation+event.",
            status_code=303
        )

    # ADMIN USER ACCESS GRANTED
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, is_locked, created_at FROM users")
    users_list = [dict(u) for u in cursor.fetchall()]
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "username": str(user["username"]),
            "users": users_list,
            "total_users": len(users_list),
            "total_incidents": len(system_state.incidents)
        }
    )

# ---------------- APPLICATION SEARCH (SQL Injection Pattern Test) ----------------
@router.post("/api/search")
def search_database(req: SearchQuerySchema, request: Request):
    source_ip = request.client.host if request.client else "192.168.1.101"
    query = req.query

    # Inspect payload for SQL Injection patterns using detector
    det_res = detector.check_sql(query, source_ip)
    if det_res.get("detected"):
        log_event("WARNING", "SQL_INJECTION_DETECTED", f"SQL Injection pattern detected in search query: '{query}'", source="SecurityFilter")
        
        # Trigger WatchCloud SQL Injection Incident Pipeline
        sim_data = {
            "source_ip": source_ip,
            "payload": query
        }
        coordinator_agent.handle_incident_simulation("sql", sim_data)

        return JSONResponse(status_code=400, content={
            "blocked": True,
            "detail": f"Security Alert: Malicious SQL injection pattern detected in input '{query}'. Request rejected by WatchCloud filter."
        })

    return {
        "blocked": False,
        "query": query,
        "message": f"Search completed safely for term '{query}'. 0 records returned."
    }

# ---------------- WATCHCLOUD MONITORING DASHBOARD & APIS ----------------
@router.get("/dashboard", response_class=HTMLResponse)
def get_watchcloud_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

@router.get("/api/incidents")
def get_incidents():
    return {
        "total_incidents": len(system_state.incidents),
        "incidents": system_state.incidents
    }

@router.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    inc = incident_manager.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return inc

@router.get("/api/logs")
def get_logs():
    return {
        "total_logs": len(system_state.logs),
        "recent_logs": system_state.logs[:50]
    }

@router.get("/api/system/status")
def system_status():
    m = collect_metrics()
    total_incidents = len(system_state.incidents)
    resolved = sum(1 for i in system_state.incidents if i.get("status") == "RESOLVED")
    in_progress = sum(1 for i in system_state.incidents if i.get("status") == "IN_PROGRESS")
    detected = sum(1 for i in system_state.incidents if i.get("status") == "DETECTED")

    return {
        "system_status": "HEALTHY",
        "active_protections": {
            "blocked_ips": list(system_state.blocked_ips),
            "locked_accounts": list(system_state.locked_accounts),
            "rate_limit_active": system_state.rate_limit_active
        },
        "incident_summary": {
            "total": total_incidents,
            "detected": detected,
            "in_progress": in_progress,
            "resolved": resolved
        },
        "current_metrics": m
    }

@router.get("/api/agents/status")
def get_agents_status():
    return {
        "agent_activities": system_state.agent_activities[:10]
    }

# ---------------- SAFE INTERNAL TEST ENDPOINTS ----------------
@router.post("/api/test/ddos")
@router.post("/simulate/ddos")
def test_ddos(req: SimulationRequest = SimulationRequest()):
    sim_data = {
        "source_ip": req.source_ip or "192.168.1.100",
        "request_count": req.request_count or 60
    }
    return coordinator_agent.handle_incident_simulation("ddos", sim_data)

@router.post("/api/test/sql-injection")
@router.post("/simulate/sql-injection")
def test_sql(req: SimulationRequest = SimulationRequest()):
    sim_data = {
        "source_ip": req.source_ip or "192.168.1.101",
        "payload": req.payload or "' OR 1=1; DROP TABLE users;--"
    }
    return coordinator_agent.handle_incident_simulation("sql", sim_data)

@router.post("/api/test/brute-force")
@router.post("/simulate/brute-force")
def test_brute_force(req: SimulationRequest = SimulationRequest()):
    sim_data = {
        "source_ip": req.source_ip or "192.168.1.102",
        "username": req.username or "user",
        "failed_count": 5
    }
    return coordinator_agent.handle_incident_simulation("brute_force", sim_data)

@router.post("/api/test/privilege-escalation")
@router.post("/simulate/privilege-escalation")
def test_privilege(req: SimulationRequest = SimulationRequest()):
    sim_data = {
        "source_ip": req.source_ip or "192.168.1.103",
        "username": req.username or "user",
        "current_role": req.current_role or "USER",
        "target_role": req.target_role or "ADMIN"
    }
    return coordinator_agent.handle_incident_simulation("privilege", sim_data)
