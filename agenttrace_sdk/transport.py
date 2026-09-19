from __future__ import annotations

from typing import Any

import httpx


class AgentTraceTransportError(RuntimeError):
    """Raised when the AgentTrace API cannot be reached successfully."""


class AgentTraceTransport:
    """
    Small synchronous HTTP transport used by the SDK.

    The SDK intentionally uses httpx directly rather than coupling itself
    to FastAPI internals.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 10.0,
        verify: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify = verify

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.headers = headers

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def post(
        self,
        path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            with httpx.Client(
                timeout=self.timeout,
                verify=self.verify,
                headers=self.headers,
            ) as client:
                response = client.post(
                    self._url(path),
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AgentTraceTransportError(
                f"Unable to reach AgentTrace API: {exc}"
            ) from exc

        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text

            raise AgentTraceTransportError(
                f"AgentTrace API returned HTTP "
                f"{response.status_code}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise AgentTraceTransportError(
                "AgentTrace API returned a non-JSON response."
            ) from exc

    def health(self) -> dict[str, Any]:
        try:
            with httpx.Client(
                timeout=self.timeout,
                verify=self.verify,
                headers=self.headers,
            ) as client:
                response = client.get(
                    self._url("/health/live")
                )
        except httpx.HTTPError as exc:
            raise AgentTraceTransportError(
                f"Unable to reach AgentTrace API: {exc}"
            ) from exc

        if response.status_code >= 400:
            raise AgentTraceTransportError(
                f"AgentTrace health check failed with "
                f"HTTP {response.status_code}."
            )

        try:
            return response.json()
        except ValueError as exc:
            raise AgentTraceTransportError(
                "AgentTrace health endpoint returned invalid JSON."
            ) from exc