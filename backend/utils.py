import json
import os
from datetime import datetime, timezone
from backend.config import LOG_FILE_PATH, INCIDENTS_FILE, LOGS_FILE

def get_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def add_log_entry(level: str, event: str, message: str, source: str = "app", metadata: dict = None) -> dict:
    if metadata is None:
        metadata = {}
    
    log_data = {
        "timestamp": get_timestamp(),
        "level": level.upper(),
        "event": event,
        "message": message,
        "source": source,
        "metadata": metadata
    }

    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{log_data['timestamp']}] [{log_data['level']}] [{log_data['event']}] {log_data['message']}\n")
    except Exception as e:
        print(f"Error writing to app.log: {e}")

    return log_data

def load_json_file(file_path: str, default_val=None):
    if default_val is None:
        default_val = []
    if not os.path.exists(file_path):
        return default_val
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def save_json_file(file_path: str, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")
