# WatchCloud – Self-Healing Cloud Infrastructure Using Multi-Agent AI

## 📌 Project Overview
**WatchCloud** is an autonomous self-healing cloud infrastructure monitoring and remediation platform built using FastAPI and Python. It continuously monitors cloud application health, detects predefined security incidents, performs root cause analysis, automatically applies safe application-level remediation, verifies resolution, and generates detailed incident reports.

---

## 🎯 Problem Statement & Objective
* **Problem**: Traditional cloud monitoring tools generate alerts when incidents occur, requiring human DevOps engineers to manually diagnose and fix problems, leading to high Downtime (MTTR - Mean Time to Resolution).
* **Objective**: Build an autonomous, self-healing cloud system using a Multi-Agent AI framework to detect, analyze, remediate, verify, and document cloud incidents automatically in seconds without manual intervention.

---

## 🏗️ System Architecture

```text
User / Browser (http://13.49.0.1:8000/)
     │
     ▼
AWS EC2 Instance (Amazon Linux 2023)
     │
     ▼
WatchCloud FastAPI Server (Port 8000)
     │
     ├─► System Monitoring (psutil metrics)
     ├─► Live Application Logging (app.log)
     │
     └─► Multi-Agent AI Pipeline
          │
          ├── [1] Detection Agent      ── (DDoS, SQLi, Brute Force, PrivEsc)
          ├── [2] Root Cause Agent     ── (RAG Knowledge Base + LLM/Demo Mode)
          ├── [3] Remediation Agent    ── (Safe application-level self-healing)
          ├── [4] Verification Agent   ── (Before/After condition verification)
          └── [5] Reporting Agent      ── (Structured incident report generation)
```

---

## 💡 Multi-Agent AI System Roles
1. **Coordinator Agent**: Orchestrates the autonomous pipeline end-to-end.
2. **Detection Agent**: Monitors log streams and metrics to detect threshold breaches and anomaly signatures.
3. **Root Cause Agent**: Performs RAG lookup against historical incidents and utilizes LLM (or rule-based Demo Mode) to determine the probable cause.
4. **Remediation Agent**: Executes safe, non-destructive remediation actions (e.g. rate-limiting, IP filtering, account locking, role restoration).
5. **Verification Agent**: Verifies whether the incident condition has returned to a normal state post-remediation.
6. **Reporting Agent**: Compiles comprehensive incident summary reports for administrators and HOD evaluation.

---

## 🚨 Detectable & Remediated Incidents
1. **DDoS / Abnormal Traffic**: Detects request frequency spikes (>20 req/s suspicious, >50 req/s critical). **Remediation**: Applies rate-limiting and temporary source IP isolation.
2. **SQL Injection**: Detects SQL keywords (`UNION SELECT`, `' OR 1=1`, `DROP TABLE`). **Remediation**: Rejects malicious payload and restricts payload sender.
3. **Brute Force**: Tracks consecutive authentication failures (5 failures). **Remediation**: Temporarily locks targeted user account and resets failure counters.
4. **Privilege Escalation**: Detects unauthorized role changes (`normal_user` -> `admin`). **Remediation**: Denies unauthorized role change and restores original role.

---

## ☁️ Why AWS EC2 is Used
AWS EC2 provides the cloud virtual server (`watchcloud-server` on `13.49.0.1`) where the application runs continuously in a real cloud environment. EC2 is the host environment being monitored and protected by WatchCloud, demonstrating real-world cloud hosting capability rather than running only on localhost.

---

## 🚀 How to Run Locally (Windows PowerShell)

### 1. Navigate to Project Directory
```powershell
cd "c:\Users\mudigonda akitha\watchcloud"
```

### 2. Activate Virtual Environment & Install Dependencies
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run Application
```powershell
python app.py
```

### 4. Access URLs in Browser
* **Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
* **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🌐 How to Deploy on AWS EC2 (Amazon Linux 2023)

### 1. SSH into EC2 Instance (from Windows PowerShell)
```powershell
ssh -i "$HOME\Downloads\watchcloud-key.pem" ec2-user@13.49.0.1
```

### 2. Setup Project & Virtual Environment on EC2
```bash
cd ~
cd watchcloud
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Application as Background Systemd Service
```bash
sudo cp watchcloud.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable watchcloud
sudo systemctl start watchcloud
sudo systemctl status watchcloud
```

### 4. View Live Logs on EC2
```bash
journalctl -u watchcloud -f
```

### 5. Access EC2 Public URL in Browser
* **EC2 Public Dashboard**: [http://13.49.0.1:8000/dashboard](http://13.49.0.1:8000/dashboard)

---

## 🎓 HOD / College Guide Demonstration Workflow
1. Open the WatchCloud Dashboard at `http://13.49.0.1:8000/dashboard` (or `http://127.0.0.1:8000/dashboard` locally).
2. Point out live **CPU, Memory, Disk, and Network** cards.
3. Click any simulation button (e.g. **Simulate Brute Force**).
4. Demonstrate the multi-agent self-healing sequence:
   * **Incident Detected**: High severity incident created (`INC-0001`).
   * **Root Cause Analyzed**: RAG retrieves past incident `KB-003` & rule-based engine identifies brute-force pattern.
   * **Remediation Executed**: Account `admin_user` locked safely & counter reset.
   * **Verification**: Verification Agent confirms zero new failed login attempts.
   * **Incident Report**: Popup modal displays complete structured incident report.
