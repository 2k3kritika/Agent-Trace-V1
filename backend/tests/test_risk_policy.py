from app.domain.detection.models import DetectionFinding
from app.domain.events.types import EventSeverity, EventType
from app.domain.policy.models import PolicyEvaluationContext
from app.domain.risk.models import RiskContext
from app.services.policy_service import PolicyService
from app.services.risk_service import RiskService


def make_finding(
    detector_id: str,
    *,
    severity: EventSeverity = EventSeverity.HIGH,
    event_id: str = "evt-test",
    confidence: float = 1.0,
) -> DetectionFinding:
    return DetectionFinding(
        detector_id=detector_id,
        event_id=event_id,
        event_type=EventType.PROMPT_INJECTION_DETECTED,
        severity=severity,
        title=f"Test finding: {detector_id}",
        description="Test detection finding",
        confidence=confidence,
    )


def make_policy_context(
    *,
    event_id: str = "evt-test",
    tool: str | None = None,
    sensitive_action: bool = False,
    prompt_injection_detected: bool = False,
    untrusted_content: bool = False,
    external_transmission: bool = False,
) -> PolicyEvaluationContext:
    return PolicyEvaluationContext(
        event_id=event_id,
        event_type="TOOL_CALL",
        tool=tool,
        sensitive_action=sensitive_action,
        prompt_injection_detected=prompt_injection_detected,
        untrusted_content=untrusted_content,
        external_transmission=external_transmission,
    )


def test_policy_allows_normal_event():
    context = make_policy_context()

    decision = PolicyService().evaluate(context)

    assert decision.allowed is True
    assert decision.blocked is False
    assert decision.decision == "ALLOW"
    assert decision.matched_rules == []


def test_policy_blocks_sensitive_action():
    context = make_policy_context(
        tool="send_email",
        sensitive_action=True,
    )

    decision = PolicyService().evaluate(context)

    assert decision.blocked is True
    assert decision.allowed is False
    assert decision.decision == "DENY"
    assert "BLOCK_SENSITIVE_ACTION" in decision.matched_rules


def test_policy_blocks_sensitive_action_with_prompt_injection():
    context = make_policy_context(
        tool="send_email",
        sensitive_action=True,
        prompt_injection_detected=True,
    )

    decision = PolicyService().evaluate(context)

    assert decision.blocked is True
    assert decision.decision == "DENY"
    assert "BLOCK_SENSITIVE_ACTION" in decision.matched_rules
    assert "BLOCK_PROMPT_INJECTION_CHAIN" in decision.matched_rules


def test_policy_blocks_sensitive_action_with_untrusted_content():
    context = make_policy_context(
        tool="send_email",
        sensitive_action=True,
        untrusted_content=True,
    )

    decision = PolicyService().evaluate(context)

    assert decision.blocked is True
    assert decision.decision == "DENY"
    assert "BLOCK_SENSITIVE_ACTION" in decision.matched_rules
    assert "BLOCK_UNTRUSTED_CONTENT_CHAIN" in decision.matched_rules


def test_policy_blocks_external_transmission():
    context = make_policy_context(
        tool="http_post",
        external_transmission=True,
    )

    decision = PolicyService().evaluate(context)

    assert decision.blocked is True
    assert decision.decision == "DENY"
    assert "BLOCK_EXTERNAL_TRANSMISSION" in decision.matched_rules


def test_should_block_matches_policy_decision():
    context = make_policy_context(
        tool="send_email",
        sensitive_action=True,
    )

    service = PolicyService()

    decision = service.evaluate(context)

    assert service.should_block(context) == decision.blocked


def test_risk_assessment_for_prompt_injection():
    finding = make_finding(
        "PROMPT_INJECTION_DETECTED",
        severity=EventSeverity.HIGH,
    )

    assessment = RiskService().assess_findings_for_hero_demo(
        [finding]
    )

    assert assessment.score > 0
    assert assessment.level in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    assert len(assessment.contributions) == 1
    assert assessment.contributions[0].source_id == (
        "PROMPT_INJECTION_DETECTED"
    )


def test_risk_assessment_for_sensitive_action():
    finding = make_finding(
        "SENSITIVE_ACTION_ATTEMPTED",
        severity=EventSeverity.HIGH,
    )

    context = RiskContext(
        sensitive_action_attempted=True,
    )

    assessment = RiskService().assess_findings_for_hero_demo(
        [finding],
        context=context,
    )

    assert assessment.score > 0
    assert any(
        "sensitive action" in factor.lower()
        for factor in assessment.factors
    )


def test_risk_assessment_increases_for_contextual_risk():
    finding = make_finding(
        "SENSITIVE_ACTION_ATTEMPTED",
        severity=EventSeverity.HIGH,
    )

    base = RiskService().assess_findings_for_hero_demo(
        [finding],
        context=RiskContext(),
    )

    elevated = RiskService().assess_findings_for_hero_demo(
        [finding],
        context=RiskContext(
            policy_violation=True,
            sensitive_action_executed=True,
            external_transmission=True,
            action_blocked=True,
        ),
    )

    assert elevated.score > base.score


def test_risk_score_is_capped_at_100():
    findings = [
        make_finding(
            "PROMPT_INJECTION_DETECTED",
            severity=EventSeverity.CRITICAL,
            event_id="evt-1",
        ),
        make_finding(
            "SENSITIVE_ACTION_ATTEMPTED",
            severity=EventSeverity.CRITICAL,
            event_id="evt-2",
        ),
        make_finding(
            "UNTRUSTED_CONTENT",
            severity=EventSeverity.CRITICAL,
            event_id="evt-3",
        ),
    ]

    assessment = RiskService().assess_findings_for_hero_demo(
        findings,
        context=RiskContext(
            policy_violation=True,
            sensitive_action_executed=True,
            external_transmission=True,
            action_blocked=True,
        ),
    )

    assert assessment.score == 100
    assert assessment.level == "CRITICAL"


def test_empty_findings_produce_low_risk():
    assessment = RiskService().assess_findings_for_hero_demo([])

    assert assessment.score == 0
    assert assessment.level == "LOW"
    assert assessment.contributions == []