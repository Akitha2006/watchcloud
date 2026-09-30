let currentIncidents = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchMetrics();
    fetchStatus();
    loadIncidents();
    loadLogs();
    fetchAgentStatus();

    setInterval(fetchMetrics, 3000);
    setInterval(fetchStatus, 3000);
    setInterval(loadIncidents, 3000);
    setInterval(loadLogs, 3000);
    setInterval(fetchAgentStatus, 3000);
});

async function fetchMetrics() {
    try {
        const res = await fetch('/metrics');
        const data = await res.json();
        
        document.getElementById('cpu-val').innerText = `${data.cpu}%`;
        document.getElementById('cpu-bar').style.width = `${data.cpu}%`;

        document.getElementById('memory-val').innerText = `${data.memory}%`;
        document.getElementById('memory-bar').style.width = `${data.memory}%`;

        document.getElementById('disk-val').innerText = `${data.disk}%`;
        document.getElementById('disk-bar').style.width = `${data.disk}%`;

        const recvKB = Math.round(data.network_received / 1024);
        const sentKB = Math.round(data.network_sent / 1024);
        document.getElementById('net-val').innerText = `${recvKB} KB`;
        document.getElementById('net-sent').innerText = `Sent: ${sentKB} KB`;
    } catch (err) {
        console.error('Error fetching metrics:', err);
    }
}

async function fetchStatus() {
    try {
        const res = await fetch('/api/system/status');
        const data = await res.json();
        
        const summary = data.incident_summary;
        document.getElementById('count-total').innerText = summary.total;
        document.getElementById('count-detected').innerText = summary.detected;
        document.getElementById('count-progress').innerText = summary.in_progress;
        document.getElementById('count-resolved').innerText = summary.resolved;
    } catch (err) {
        console.error('Error fetching status:', err);
    }
}

async function fetchAgentStatus() {
    try {
        const res = await fetch('/api/agents/status');
        const data = await res.json();
        const activities = data.agent_activities || [];
        
        if (activities.length > 0) {
            const pipelineStatusEl = document.getElementById('agent-pipeline-status');
            pipelineStatusEl.innerText = "ACTIVE";
            pipelineStatusEl.className = "badge badge-MEDIUM";

            // Map agent statuses
            const agentMap = {
                "Detection Agent": "step-detection",
                "Root Cause Agent": "step-rootcause",
                "RAG Service": "step-rag",
                "Remediation Agent": "step-remediation",
                "Verification Agent": "step-verification",
                "Reporting Agent": "step-reporting"
            };

            const statusTextMap = {
                "Detection Agent": "status-detection",
                "Root Cause Agent": "status-rootcause",
                "RAG Service": "status-rag",
                "Remediation Agent": "status-remediation",
                "Verification Agent": "status-verification",
                "Reporting Agent": "status-reporting"
            };

            activities.forEach(act => {
                const stepId = agentMap[act.agent];
                const textId = statusTextMap[act.agent];
                if (stepId && textId) {
                    const stepEl = document.getElementById(stepId);
                    const txtEl = document.getElementById(textId);
                    stepEl.className = `agent-step status-${act.status.toLowerCase()}`;
                    txtEl.innerText = act.status;
                }
            });
        }
    } catch (err) {
        console.error('Error fetching agent status:', err);
    }
}

async function loadIncidents() {
    try {
        const res = await fetch('/api/incidents');
        const data = await res.json();
        currentIncidents = data.incidents || [];
        renderIncidentsTable(currentIncidents);
        renderLatestIncidentCard(currentIncidents);
    } catch (err) {
        console.error('Error loading incidents:', err);
    }
}

function renderIncidentsTable(incidents) {
    const tbody = document.getElementById('incidents-tbody');
    if (!incidents || incidents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No incidents recorded yet.</td></tr>';
        return;
    }

    tbody.innerHTML = incidents.map(inc => `
        <tr>
            <td><strong>${inc.incident_id}</strong></td>
            <td>${inc.type}</td>
            <td><span class="badge badge-${inc.severity}">${inc.severity}</span></td>
            <td>${inc.timestamp}</td>
            <td><span class="badge badge-${inc.status}">${inc.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="openReportModal('${inc.incident_id}')">📄 View Report</button>
            </td>
        </tr>
    `).join('');
}

function renderLatestIncidentCard(incidents) {
    const container = document.getElementById('active-incident-details');
    const badge = document.getElementById('active-inc-badge');

    if (!incidents || incidents.length === 0) {
        badge.className = 'badge badge-RESOLVED';
        badge.innerText = 'NO ACTIVE INCIDENTS';
        container.innerHTML = '<p style="color: var(--text-secondary);">System operating under nominal parameters. No active security incidents detected.</p>';
        return;
    }

    const latest = incidents[0];
    badge.className = `badge badge-${latest.status}`;
    badge.innerText = `LATEST: ${latest.status}`;

    container.innerHTML = `
        <div style="line-height: 1.6;">
            <p><strong>Incident ID:</strong> <code>${latest.incident_id}</code></p>
            <p><strong>Type:</strong> ${latest.type} &nbsp;|&nbsp; <strong>Severity:</strong> <span class="badge badge-${latest.severity}">${latest.severity}</span></p>
            <p><strong>Detected At:</strong> ${latest.timestamp}</p>
            <p><strong>Description:</strong> ${latest.description}</p>
            <p><strong>Root Cause:</strong> <span style="color: var(--accent-yellow);">${latest.possible_cause || 'Analyzing...'}</span></p>
            <p><strong>Remediation:</strong> ${latest.remediation || 'Pending action...'}</p>
            <p><strong>Verification:</strong> <span style="color: var(--accent-green);">${latest.verification || 'Pending verification...'}</span></p>
            <div style="margin-top: 10px;">
                <button class="btn btn-sm btn-primary" onclick="openReportModal('${latest.incident_id}')">📄 Open Incident Report</button>
            </div>
        </div>
    `;
}

async function loadLogs() {
    try {
        const res = await fetch('/api/logs');
        const data = await res.json();
        const logs = data.recent_logs || [];
        const consoleEl = document.getElementById('logs-console');
        
        consoleEl.innerHTML = logs.map(l => `
            <div class="log-line log-${l.level}">
                [${l.timestamp}] [${l.level}] [${l.source}] ${l.message}
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading logs:', err);
    }
}

async function openReportModal(incidentOrId) {
    const modal = document.getElementById('report-modal');
    const titleEl = document.getElementById('modal-title');
    const textEl = document.getElementById('modal-report-text');

    let inc = null;
    if (typeof incidentOrId === 'object' && incidentOrId !== null) {
        inc = incidentOrId;
    } else if (typeof incidentOrId === 'string') {
        inc = currentIncidents.find(i => i.incident_id === incidentOrId);
        if (!inc) {
            try {
                const res = await fetch(`/api/incidents/${incidentOrId}`);
                inc = await res.json();
            } catch (err) {
                console.error("Error fetching incident detail:", err);
            }
        }
    }

    if (inc && inc.incident_id) {
        titleEl.innerText = `WatchCloud Incident Report - ${inc.incident_id}`;
        textEl.innerText = inc.report || `WATCHCLOUD INCIDENT REPORT\nIncident ID: ${inc.incident_id}\nType: ${inc.type}\nSeverity: ${inc.severity}\nStatus: ${inc.status}\n\nDescription:\n${inc.description}\n\nPossible Cause:\n${inc.possible_cause}\n\nRemediation Action:\n${inc.remediation}\n\nVerification:\n${inc.verification}`;
    } else {
        titleEl.innerText = `WatchCloud Incident Report`;
        textEl.innerText = 'Unable to retrieve incident details. Please try again.';
    }

    modal.classList.add('active');
}

function closeModal(event) {
    if (event.target.id === 'report-modal') {
        closeModalDirect();
    }
}

function closeModalDirect() {
    document.getElementById('report-modal').classList.remove('active');
}
