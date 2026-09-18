from __future__ import annotations

from app.domain.events.types import EventSeverity
from app.domain.policy.models import (
    PolicyDecision,
    PolicyEvaluationContext,
)


class PolicyService:
    """
    Deterministic policy evaluation service.

    The initial policy engine contains the security controls required for
    the AgentTrace controlled demonstration.

    Policies are provider-neutral and operate on a normalized evaluation
    context rather than directly on provider-specific telemetry.
    """

    DEFAULT_POLICY_ID = "policy-sensitive-action-protection"
    DEFAULT_POLICY_NAME = "Sensitive Action Protection"

    def evaluate(
        self,
        context: PolicyEvaluationContext,
    ) -> PolicyDecision:
        """
        Evaluate one event/action against the active security policy.

        Evaluation order matters. The strongest security conditions are
        checked first so that a suspicious instruction cannot turn into an
        allowed sensitive action merely because the individual event itself
        looks ordinary.
        """

        matched_rules: list[str] = []

        if context.external_transmission:
            matched_rules.append("BLOCK_EXTERNAL_TRANSMISSION")

            return PolicyDecision(
                decision="DENY",
                policy_id=self.DEFAULT_POLICY_ID,
                policy_name=self.DEFAULT_POLICY_NAME,
                reason=(
                    "External data transmission is prohibited by the "
                    "active security policy."
                ),
                severity=EventSeverity.CRITICAL,
                matched_rules=matched_rules,
                event_id=context.event_id,
                tool=context.tool,
                metadata={
                    "policy_action": "DENY",
                    "control": "external_transmission",
                },
            )

        if context.sensitive_action and context.prompt_injection_detected:
            matched_rules.extend(
                [
                    "BLOCK_SENSITIVE_ACTION",
                    "BLOCK_PROMPT_INJECTION_CHAIN",
                ]
            )

            return PolicyDecision(
                decision="DENY",
                policy_id=self.DEFAULT_POLICY_ID,
                policy_name=self.DEFAULT_POLICY_NAME,
                reason=(
                    "A sensitive action was attempted in a context "
                    "containing a detected prompt-injection signal."
                ),
                severity=EventSeverity.CRITICAL,
                matched_rules=matched_rules,
                event_id=context.event_id,
                tool=context.tool,
                metadata={
                    "policy_action": "DENY",
                    "control": "prompt_injection_sensitive_action",
                },
            )

        if context.sensitive_action and context.untrusted_content:
            matched_rules.extend(
                [
                    "BLOCK_SENSITIVE_ACTION",
                    "BLOCK_UNTRUSTED_CONTENT_CHAIN",
                ]
            )

            return PolicyDecision(
                decision="DENY",
                policy_id=self.DEFAULT_POLICY_ID,
                policy_name=self.DEFAULT_POLICY_NAME,
                reason=(
                    "A sensitive action was attempted after processing "
                    "untrusted content."
                ),
                severity=EventSeverity.HIGH,
                matched_rules=matched_rules,
                event_id=context.event_id,
                tool=context.tool,
                metadata={
                    "policy_action": "DENY",
                    "control": "untrusted_content_sensitive_action",
                },
            )

        if context.sensitive_action:
            matched_rules.append("BLOCK_SENSITIVE_ACTION")

            return PolicyDecision(
                decision="DENY",
                policy_id=self.DEFAULT_POLICY_ID,
                policy_name=self.DEFAULT_POLICY_NAME,
                reason=(
                    "Sensitive actions require explicit authorization "
                    "under the active security policy."
                ),
                severity=EventSeverity.HIGH,
                matched_rules=matched_rules,
                event_id=context.event_id,
                tool=context.tool,
                metadata={
                    "policy_action": "DENY",
                    "control": "sensitive_action",
                },
            )

        return PolicyDecision(
            decision="ALLOW",
            policy_id=self.DEFAULT_POLICY_ID,
            policy_name=self.DEFAULT_POLICY_NAME,
            reason="No active security policy prohibited this action.",
            severity=EventSeverity.LOW,
            matched_rules=[],
            event_id=context.event_id,
            tool=context.tool,
            metadata={
                "policy_action": "ALLOW",
            },
        )

    def should_block(
        self,
        context: PolicyEvaluationContext,
    ) -> bool:
        """
        Convenience method used by action-control flows.
        """

        return self.evaluate(context).blocked