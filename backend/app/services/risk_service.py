from __future__ import annotations

from collections.abc import Iterable

from app.domain.detection.models import DetectionFinding
from app.domain.events.types import EventSeverity
from app.domain.risk.models import (
    RiskAssessment,
    RiskContext,
    RiskContribution,
)


class RiskService:
    """
    Deterministic, explainable risk scoring service.

    Risk scoring is intentionally rule-based at this stage. The hackathon
    needs predictable behavior for the controlled demo, and deterministic
    scoring makes the displayed risk score auditable.
    """

    _severity_points = {
        EventSeverity.LOW: 5,
        EventSeverity.MEDIUM: 15,
        EventSeverity.HIGH: 25,
        EventSeverity.CRITICAL: 40,
    }

    _detector_points = {
        "UNTRUSTED_CONTENT": 10,
        "PROMPT_INJECTION_DETECTED": 30,
        "SENSITIVE_ACTION_ATTEMPTED": 30,
    }

    def assess_findings(
        self,
        findings: Iterable[DetectionFinding],
        context: RiskContext | None = None,
    ) -> RiskAssessment:
        context = context or RiskContext()

        contributions: list[RiskContribution] = []

        for finding in findings:
            points = self._calculate_finding_points(finding)

            contributions.append(
                RiskContribution(
                    source_id=finding.detector_id,
                    source_type="DETECTION",
                    description=finding.title,
                    points=points,
                    severity=finding.severity,
                    event_id=finding.event_id,
                    metadata={
                        "confidence": finding.confidence,
                        **finding.metadata,
                    },
                )
            )

        self._add_context_contributions(
            contributions,
            context,
        )

        raw_score = sum(
            contribution.points
            for contribution in contributions
        )

        score = min(raw_score, 100)

        factors = self._build_factors(
            contributions,
            context,
        )

        return RiskAssessment(
            score=score,
            level=self._risk_level(score),
            contributions=contributions,
            factors=factors,
            metadata={
                "raw_score": raw_score,
                "contribution_count": len(contributions),
            },
        )

    def assess_findings_for_hero_demo(
        self,
        findings: Iterable[DetectionFinding],
        context: RiskContext | None = None,
    ) -> RiskAssessment:
        """
        Score the controlled demo using the same explainable model.

        The hero scenario is designed around:
            untrusted content
            + prompt injection
            + sensitive action
            + policy violation
            + blocked action

        The explicit context factors make the resulting score stable rather
        than dependent on incidental event ordering.
        """

        return self.assess_findings(
            findings=findings,
            context=context,
        )

    def _calculate_finding_points(
        self,
        finding: DetectionFinding,
    ) -> int:
        detector_points = self._detector_points.get(
            finding.detector_id,
            0,
        )

        severity_points = self._severity_points.get(
            finding.severity,
            0,
        )

        confidence_multiplier = max(
            0.5,
            min(1.0, finding.confidence),
        )

        # Detector-specific points carry most of the weight. Severity adds
        # context without allowing a single low-confidence finding to
        # dominate the entire assessment.
        points = (
            detector_points
            + int(severity_points * confidence_multiplier)
        )

        return max(1, points)

    def _add_context_contributions(
        self,
        contributions: list[RiskContribution],
        context: RiskContext,
    ) -> None:
        if context.policy_violation:
            contributions.append(
                RiskContribution(
                    source_id="POLICY_VIOLATION",
                    source_type="POLICY",
                    description="Security policy violation",
                    points=15,
                    severity=EventSeverity.HIGH,
                )
            )

        if context.sensitive_action_executed:
            contributions.append(
                RiskContribution(
                    source_id="SENSITIVE_ACTION_EXECUTED",
                    source_type="ACTION",
                    description="Sensitive action was executed",
                    points=20,
                    severity=EventSeverity.CRITICAL,
                )
            )

        if context.external_transmission:
            contributions.append(
                RiskContribution(
                    source_id="EXTERNAL_TRANSMISSION",
                    source_type="ACTION",
                    description="Data was transmitted externally",
                    points=20,
                    severity=EventSeverity.CRITICAL,
                )
            )

        if context.action_blocked:
            contributions.append(
                RiskContribution(
                    source_id="ACTION_BLOCKED",
                    source_type="POLICY",
                    description="Sensitive action was blocked",
                    points=5,
                    severity=EventSeverity.MEDIUM,
                )
            )

    def _build_factors(
        self,
        contributions: list[RiskContribution],
        context: RiskContext,
    ) -> list[str]:
        factors: list[str] = []

        seen: set[str] = set()

        for contribution in contributions:
            factor = contribution.description

            if factor not in seen:
                factors.append(factor)
                seen.add(factor)

        if context.sensitive_action_attempted:
            if "Sensitive action attempted" not in seen:
                factors.append("Sensitive action attempted")

        if context.policy_violation:
            if "Policy violation" not in seen:
                factors.append("Policy violation")

        if context.action_blocked:
            if "Action blocked by policy" not in seen:
                factors.append("Action blocked by policy")

        if context.external_transmission:
            if "External transmission" not in seen:
                factors.append("External transmission")

        return factors

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 80:
            return "CRITICAL"

        if score >= 60:
            return "HIGH"

        if score >= 30:
            return "MEDIUM"

        return "LOW"