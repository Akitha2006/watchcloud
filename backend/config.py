import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "WatchCloud")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Detector Thresholds
DDOS_SUSPICIOUS_THRESHOLD = 20  # requests per window
DDOS_CRITICAL_THRESHOLD = 50

BRUTE_FORCE_WARNING_LIMIT = 3
BRUTE_FORCE_INCIDENT_LIMIT = 5

# Security SQL Patterns
SQL_INJECTION_PATTERNS = [
    "' OR",
    "UNION SELECT",
    "DROP TABLE",
    ";--",
    "OR 1=1",
    "--",
    "/*"
]

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INCIDENTS_FILE = os.path.join(DATA_DIR, "incidents.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
KNOWLEDGE_BASE_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
LOG_FILE_PATH = os.path.join(BASE_DIR, "app.log")

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
