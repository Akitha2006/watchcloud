from backend.utils import add_log_entry
from backend.state import system_state

def log_event(level: str, event: str, message: str, source: str = "app", metadata: dict = None):
    log_data = add_log_entry(level, event, message, source, metadata)
    system_state.add_log(log_data)
    return log_data
