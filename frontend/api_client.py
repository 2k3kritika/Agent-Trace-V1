from __future__ import annotations

from typing import Any

import requests

from config import API_BASE_URL, REQUEST_TIMEOUT


class AgentTraceAPI:
    """Client for communicating with the AgentTrace FastAPI backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any] | list[Any] | None:
        url = f"{self.base_url}{endpoint}"

        kwargs.setdefault("timeout", REQUEST_TIMEOUT)

        try:
            response = self.session.request(
                method,
                url,
                **kwargs,
            )

            response.raise_for_status()

            if not response.content:
                return None

            return response.json()

        except requests.RequestException as exc:
            raise RuntimeError(
                f"AgentTrace API request failed: {exc}"
            ) from exc

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def health(self) -> dict[str, Any]:
        result = self._request("GET", "/health")
        return result or {}

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------

    def dashboard_overview(self) -> dict[str, Any]:
        result = self._request("GET", "/dashboard/overview")
        return result or {}

    # ---------------------------------------------------------
    # Agents
    # ---------------------------------------------------------

    def get_agents(self) -> list[dict[str, Any]]:
        result = self._request("GET", "/agents")

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get("items", result.get("agents", []))

        return []

    def get_agent(
        self,
        agent_id: str,
    ) -> dict[str, Any]:
        result = self._request(
            "GET",
            f"/agents/{agent_id}",
        )

        return result or {}

    def get_agent_risk(
        self,
        agent_id: str,
    ) -> dict[str, Any]:
        result = self._request(
            "GET",
            f"/agents/{agent_id}/risk",
        )

        return result or {}

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------

    def get_events(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            "/events",
            params={"limit": limit},
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get("items", result.get("events", []))

        return []

    def get_security_events(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            "/events/security",
            params={"limit": limit},
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get(
                "items",
                result.get("events", []),
            )

        return []

    def get_session_events(
        self,
        session_id: str,
    ) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            f"/events/session/{session_id}",
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get(
                "items",
                result.get("events", []),
            )

        return []

    # ---------------------------------------------------------
    # Alerts
    # ---------------------------------------------------------

    def get_alerts(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            "/alerts",
            params={"limit": limit},
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get(
                "items",
                result.get("alerts", []),
            )

        return []

    # ---------------------------------------------------------
    # Investigations
    # ---------------------------------------------------------

    def get_investigations(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            "/investigations",
            params={"limit": limit},
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get(
                "items",
                result.get("investigations", []),
            )

        return []

    def get_investigation(
        self,
        investigation_id: str,
    ) -> dict[str, Any]:
        result = self._request(
            "GET",
            f"/investigations/{investigation_id}",
        )

        return result or {}

    def get_investigation_evidence(
        self,
        investigation_id: str,
    ) -> list[dict[str, Any]]:
        result = self._request(
            "GET",
            f"/evidence/investigation/{investigation_id}",
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            return result.get(
                "items",
                result.get("evidence", []),
            )

        return []

    # ---------------------------------------------------------
    # Forensics
    # ---------------------------------------------------------

    def analyze_investigation(
        self,
        investigation_id: str,
    ) -> dict[str, Any]:
        result = self._request(
            "POST",
            f"/forensics/investigations/{investigation_id}/analyze",
        )

        return result or {}

    # ---------------------------------------------------------
    # Demo
    # ---------------------------------------------------------

    def run_hero_demo(self) -> dict[str, Any]:
        result = self._request(
            "POST",
            "/demo/hero",
        )

        return result or {}

    # ---------------------------------------------------------
    # Policies
    # ---------------------------------------------------------

    def evaluate_policy(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        result = self._request(
            "POST",
            "/policies/evaluate",
            json=payload,
        )

        return result or {}