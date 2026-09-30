import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from backend.routes import router
from backend.config import BASE_DIR, HOST, PORT
from backend.database import init_db

app = FastAPI(
    title="WatchCloud Self-Healing Infrastructure & Web Application",
    description="Autonomous Cloud Infrastructure Monitoring & Remediation using Multi-Agent AI",
    version="1.0.0"
)

# Initialize SQLite database schema & seed demo users
@app.on_event("startup")
def startup_event():
    init_db()

# Mount Static Files
static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include Router
app.include_router(router)

if __name__ == "__main__":
    print("==========================================")
    print("       WATCHCLOUD SELF-HEALING SYSTEM")
    print("==========================================")
    print("Application is running!")
    print()
    print(f"Local App URL    : http://127.0.0.1:{PORT}/")
    print(f"Local Login      : http://127.0.0.1:{PORT}/login")
    print(f"WatchCloud UI    : http://127.0.0.1:{PORT}/dashboard")
    print(f"Health Check     : http://127.0.0.1:{PORT}/health")
    print(f"Metrics Endpoint : http://127.0.0.1:{PORT}/metrics")
    print(f"Swagger API Docs : http://127.0.0.1:{PORT}/docs")
    print()
    print("For AWS EC2 Deployment:")
    print("AWS EC2 Login     : http://13.49.0.1:8000/login")
    print("AWS EC2 Dashboard : http://13.49.0.1:8000/dashboard")
    print("==========================================")

    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        reload=False
    )