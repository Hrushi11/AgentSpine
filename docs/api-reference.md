# API Reference

## SDK

Current public entry points are exported from `agentspine`:

- `AgentSpine`
- `FeatureFlags`
- `ActionRequest`
- `ActionResult`
- `ActionStatus`
- `Resource`
- `RewardInput`

## Core Call

```python
result = await spine.request_action(
    action_type="custom.action",
    payload={"key": "value"},
    idempotency_key="example-001",
)
```

## Server Endpoints

- `POST /api/v1/actions`
  - submit an action request
- `GET /api/v1/actions`
  - list recent actions
- `GET /api/v1/actions/{id}`
  - get a single action and its event timeline
- `POST /api/v1/actions/{id}/replay`
  - replay a historical action as a new request
- `GET /api/v1/approvals`
  - list pending approvals
- `POST /api/v1/approvals/{id}/resolve`
  - approve or reject a pending action
- `GET /api/v1/events`
  - list event rows, optionally filtered by action id
- `POST /api/v1/events`
  - publish a custom event or report an external execution result
- `POST /api/v1/rewards`
  - record a reward signal against an action
- `GET /api/v1/policies`
  - list active policies
- `POST /api/v1/policies`
  - create or update a policy
- `DELETE /api/v1/policies/{id}`
  - delete a policy
- `GET /api/v1/workflows`
  - list stored workflow configuration rows
- `PUT /api/v1/workflows/{name}`
  - persist workflow configuration
- `GET /health`
- `GET /ready`
- `GET /metrics`

## External Execution

When no local tool is registered for an action type, AgentSpine emits a normalized execution signal.
That signal can be delivered to an external worker over webhook, HTTP, or a custom adapter.
The worker can later report the result back through:

- `POST /api/v1/events` with `event_type=external.execution_reported`
