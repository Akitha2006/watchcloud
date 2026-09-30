import psutil
from backend.utils import get_timestamp
from backend.state import system_state

def collect_metrics() -> dict:
    net_io = psutil.net_io_counters()
    
    metrics = {
        "timestamp": get_timestamp(),
        "cpu": round(psutil.cpu_percent(interval=None), 1),
        "memory": round(psutil.virtual_memory().percent, 1),
        "disk": round(psutil.disk_usage("/").percent if hasattr(psutil.disk_usage("/"), "percent") else psutil.disk_usage("C:\\").percent, 1),
        "network_sent": net_io.bytes_sent,
        "network_received": net_io.bytes_recv
    }
    
    # Store in memory history
    system_state.metrics_history.append(metrics)
    if len(system_state.metrics_history) > 60:
        system_state.metrics_history = system_state.metrics_history[-60:]

    return metrics
