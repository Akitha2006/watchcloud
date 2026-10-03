import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from monitoring.log_monitor import log_event

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_RECIPIENT_EMAIL = os.getenv("ALERT_RECIPIENT_EMAIL", "admin@watchcloud.io")

def send_incident_email(incident: dict, recipient_email: str = None) -> bool:
    if not recipient_email:
        recipient_email = ALERT_RECIPIENT_EMAIL

    subject = f"🚨 WatchCloud Security Alert: [{incident.get('severity')}] {incident.get('type')} Incident {incident.get('incident_id')}"
    body = incident.get("report") or f"Incident Report for {incident.get('incident_id')}:\nType: {incident.get('type')}\nStatus: {incident.get('status')}"

    # Log dispatch in application logs & dashboard stream
    log_event(
        "INFO",
        "EMAIL_ALERT_SENT",
        f"📧 [EMAIL ALERT DISPATCHED] Incident report for {incident.get('incident_id')} sent to {recipient_email}",
        source="EmailNotificationService",
        metadata={"recipient": recipient_email, "incident_id": incident.get("incident_id")}
    )

    if not SMTP_SERVER or not SMTP_USERNAME:
        # Demo mode / Local logging mode
        print(f"📧 [DEMO MODE EMAIL DISPATCHED to {recipient_email}]: {subject}")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Dispatch Error: {e}")
        return False
