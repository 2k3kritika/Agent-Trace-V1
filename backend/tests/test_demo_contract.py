from app.schemas.demo import DemoScenarioResponse


def test_demo_response_contract() -> None:
    response = DemoScenarioResponse.model_validate(
        {
            "scenario": "controlled_prompt_injection",
            "agent_id": "research-agent",
            "session_id": "s87f2",
            "investigation_id": "inv-hero",
            "risk_score": 85,
            "risk_level": "HIGH",
            "suspicious_events": 3,
            "sensitive_action_attempted": True,
            "sensitive_action_executed": False,
            "policy_violation": True,
            "action_blocked": True,
            "external_transmission": False,
        }
    )

    assert response.agent_id == "research-agent"
    assert response.session_id == "s87f2"
    assert response.risk_score == 85
    assert response.risk_level == "HIGH"
    assert response.sensitive_action_attempted is True
    assert response.sensitive_action_executed is False
    assert response.action_blocked is True
    assert response.external_transmission is False
