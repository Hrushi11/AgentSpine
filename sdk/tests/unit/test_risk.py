from agentspine.models import ActionRequest, Resource
from agentspine.risk.scorer import RiskScorer


async def test_risk_scorer_marks_destructive_external_actions_high():
    scorer = RiskScorer(db=None)
    request = ActionRequest(
        workflow="ops",
        agent="agent-1",
        action_type="email.delete_and_notify",
        payload={"recipient": "user@example.com", "message": "done"},
        resource=Resource(type="mailbox", id="primary"),
        context={"sensitive": True},
    )

    result = await scorer.score(request)

    assert result.score >= 0.8
    assert "destructive_action" in result.reason
    assert "external_side_effect" in result.reason
