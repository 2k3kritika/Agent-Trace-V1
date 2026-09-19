# AgentTrace

AgentTrace is an AI-agent security telemetry and forensic investigation platform.

It captures agent activity, normalizes telemetry into a canonical event model,
detects suspicious behavior, evaluates policies, calculates risk, correlates
events, builds investigations, produces forensic findings, and exposes the
results through a FastAPI backend.

## Architecture

```text
AI Agent
   |
   | telemetry
   v
Adapter / SDK
   |
   v
Canonical Event
   |
   +--> Detection
   |
   +--> Risk Assessment
   |
   +--> Policy Evaluation
   |
   v
Investigation
   |
   +--> Alerts
   +--> Evidence
   +--> Correlation
   +--> Attack Graph
   +--> Forensics
   +--> Reports
   |
   v
FastAPI API
   |
   +--> React Frontend
   +--> AgentTrace SDK
   +--> AWS API Gateway / Lambda