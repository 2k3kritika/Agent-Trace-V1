from app.domain.events.models import CanonicalEvent
from app.domain.events.types import EventRelationshipType
from app.domain.forensics.models import (
    AttackGraph,
    AttackGraphEdge,
    AttackGraphNode,
    ForensicAnalysisResult,
)
from app.domain.forensics.rules import DEFAULT_FORENSIC_RULES


class ForensicService:
    """
    Deterministic forensic analysis over canonical telemetry.

    Storage access remains outside this service. The caller supplies
    canonical events and the service produces forensic findings,
    timeline information, and an attack graph.
    """

    def analyze(
        self,
        investigation_id: str,
        events: list[CanonicalEvent],
        evidence_count: int = 0,
    ) -> ForensicAnalysisResult:
        ordered_events = sorted(
            events,
            key=lambda event: event.timestamp,
        )

        findings = []

        for rule in DEFAULT_FORENSIC_RULES:
            findings.extend(
                rule.evaluate(
                    investigation_id,
                    ordered_events,
                )
            )

        graph = self._build_attack_graph(
            ordered_events
        )

        timeline_start = (
            ordered_events[0].timestamp
            if ordered_events
            else None
        )

        timeline_end = (
            ordered_events[-1].timestamp
            if ordered_events
            else None
        )

        security_event_count = sum(
            1
            for event in ordered_events
            if event.severity.value in {"HIGH", "CRITICAL"}
            or event.event_type.value
            in {
                "UNTRUSTED_CONTENT",
                "PROMPT_INJECTION_DETECTED",
                "SENSITIVE_ACTION_ATTEMPTED",
                "POLICY_VIOLATION",
                "TOOL_BLOCKED",
            }
        )

        return ForensicAnalysisResult(
            investigation_id=investigation_id,
            findings=findings,
            graph=graph,
            evidence_count=evidence_count,
            security_event_count=security_event_count,
            timeline_start=timeline_start,
            timeline_end=timeline_end,
            summary={
                "finding_count": len(findings),
                "event_count": len(ordered_events),
                "security_event_count": security_event_count,
                "evidence_count": evidence_count,
            },
        )

    @staticmethod
    def _build_attack_graph(
        events: list[CanonicalEvent],
    ) -> AttackGraph:
        nodes: list[AttackGraphNode] = []
        edges: list[AttackGraphEdge] = []

        previous_event: CanonicalEvent | None = None

        for event in events:
            nodes.append(
                AttackGraphNode(
                    node_id=event.event_id,
                    node_type="event",
                    label=event.event_type.value,
                    event_id=event.event_id,
                    severity=event.severity.value,
                    metadata={
                        "status": event.status.value,
                        "tool": event.tool,
                        "provider": event.provider,
                    },
                )
            )

            if previous_event is not None:
                edges.append(
                    AttackGraphEdge(
                        edge_id=f"{previous_event.event_id}->{event.event_id}",
                        source=previous_event.event_id,
                        target=event.event_id,
                        relationship=EventRelationshipType.FOLLOWS.value,
                    )
                )

            previous_event = event

        return AttackGraph(
            nodes=nodes,
            edges=edges,
        )