from types import SimpleNamespace

from agentspine.models import ActionRequest, PolicyDecision, Resource
from agentspine.policy.rules import RuleEvaluator


def test_rule_evaluator_matches_action_resource_and_context():
    request = ActionRequest(
        workflow="support",
        agent="triage",
        action_type="ticket.close",
        payload={"reason": "resolved"},
        resource=Resource(type="ticket", id="T-1"),
        context={"sensitive": True},
    )
    policy = SimpleNamespace(
        name="close-sensitive-ticket",
        action="require_approval",
        condition={
            "action_types": ["ticket.close"],
            "resource_types": ["ticket"],
            "context_equals": {"sensitive": True},
        },
    )

    evaluator = RuleEvaluator()

    assert evaluator.matches(policy, request) is True
    assert evaluator.normalize_decision(policy.action) == PolicyDecision.REQUIRE_APPROVAL


def test_rule_evaluator_rejects_non_matching_action():
    request = ActionRequest(
        workflow="support",
        agent="triage",
        action_type="ticket.comment",
        payload={"text": "hello"},
    )
    policy = SimpleNamespace(
        name="deny-closing",
        action="deny",
        condition={"action_types": ["ticket.close"]},
    )

    evaluator = RuleEvaluator()
    assert evaluator.matches(policy, request) is False
