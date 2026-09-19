import os


API_BASE_URL = os.getenv(
    "AGENTTRACE_API_URL",
    "https://7ay8njoi2m.execute-api.ap-south-1.amazonaws.com/Prod",
)

APP_TITLE = "AgentTrace"
APP_SUBTITLE = "AI Agent Security Telemetry & Forensics"

REQUEST_TIMEOUT = 30

RISK_LEVELS = {
    "LOW": {
        "color": "#22c55e",
        "background": "#052e16",
    },
    "MEDIUM": {
        "color": "#eab308",
        "background": "#422006",
    },
    "HIGH": {
        "color": "#f97316",
        "background": "#431407",
    },
    "CRITICAL": {
        "color": "#ef4444",
        "background": "#450a0a",
    },
}

EVENT_TYPES = [
    "all",
    "agent.started",
    "agent.completed",
    "tool.called",
    "tool.blocked",
    "content.received",
    "security.alert",
    "policy.violation",
    "investigation.created",
]