from __future__ import annotations

from app.adapters.base import AgentAdapter


class AdapterRegistry:
    """
    Registry for AgentTrace telemetry adapters.

    The registry keeps provider-specific implementation details
    out of API routes and services.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, AgentAdapter] = {}

    def register(
        self,
        adapter: AgentAdapter,
    ) -> None:
        key = self._normalize_key(adapter.adapter_name)

        if key in self._adapters:
            raise ValueError(
                f"Adapter '{adapter.adapter_name}' is already registered."
            )

        self._adapters[key] = adapter

    def replace(
        self,
        adapter: AgentAdapter,
    ) -> None:
        key = self._normalize_key(adapter.adapter_name)
        self._adapters[key] = adapter

    def get(
        self,
        adapter_name: str,
    ) -> AgentAdapter:
        key = self._normalize_key(adapter_name)

        try:
            return self._adapters[key]
        except KeyError:
            available = ", ".join(
                sorted(self._adapters.keys())
            )

            raise KeyError(
                f"Unknown adapter '{adapter_name}'. "
                f"Available adapters: {available or 'none'}"
            ) from None

    def has(
        self,
        adapter_name: str,
    ) -> bool:
        return (
            self._normalize_key(adapter_name)
            in self._adapters
        )

    def list_adapters(self) -> list[str]:
        return sorted(self._adapters.keys())

    @staticmethod
    def _normalize_key(value: str) -> str:
        return value.strip().lower()


registry = AdapterRegistry()