from __future__ import annotations

from app.adapters.local.generic import GenericLocalAdapter
from app.adapters.gemini.gemini import GeminiAdapter
from app.adapters.local.nova import NovaAdapter
from app.adapters.local.research_agent import ResearchAgentAdapter
from app.adapters.registry import AdapterRegistry


def create_default_registry() -> AdapterRegistry:
    """
    Create the standard AgentTrace adapter registry.

    The registry contains all adapters supported by the local MVP.
    """

    registry = AdapterRegistry()

    registry.register(GenericLocalAdapter())
    registry.register(NovaAdapter())
    registry.register(ResearchAgentAdapter())
    registry.register(GeminiAdapter())

    return registry


def create_registry_with_openai_compatible() -> AdapterRegistry:
    """
    Create the standard registry plus the generic OpenAI-compatible adapter.

    The import is intentionally local so the normal registry can remain
    lightweight and avoid unnecessary coupling.
    """

    from app.adapters.custom.openai_compatible import OpenAICompatibleAdapter

    registry = create_default_registry()
    registry.register(OpenAICompatibleAdapter())

    return registry


default_registry = create_registry_with_openai_compatible()