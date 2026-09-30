import time
import requests
from monitoring.metrics import collect_metrics
from monitoring.log_monitor import log_event

CPU_LIMIT = 90
MEMORY_LIMIT = 90
DISK_LIMIT = 90

def check_system_local():
    metrics = collect_metrics()
    cpu = metrics["cpu"]
    memory = metrics["memory"]
    disk = metrics["disk"]

    print("\n[MONITOR] System Metrics Collection")
    print(f"  CPU Usage   : {cpu}%")
    print(f"  Memory Usage: {memory}%")
    print(f"  Disk Usage  : {disk}%")

    if cpu > CPU_LIMIT:
        log_event("WARNING", "HIGH_CPU", f"CPU utilization elevated: {cpu}%")
    if memory > MEMORY_LIMIT:
        log_event("WARNING", "HIGH_MEMORY", f"Memory utilization elevated: {memory}%")
    if disk > DISK_LIMIT:
        log_event("WARNING", "HIGH_DISK", f"Disk utilization elevated: {disk}%")

    return metrics

if __name__ == "__main__":
    print("Starting WatchCloud System Monitoring Worker...")
    while True:
        check_system_local()
        time.sleep(5)