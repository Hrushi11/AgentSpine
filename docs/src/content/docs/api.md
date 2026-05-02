---
title: API Reference
description: Detailed documentation of the AgentSpine SDK and Server API.
---

This reference covers the primary entry points for interacting with AgentSpine.

## Python SDK Reference

The `AgentSpine` class is the primary interface for the SDK.

### `AgentSpine`

```python
from agentspine import AgentSpine

spine = AgentSpine(
    workflow="my_workflow",
    config=None  # Optional AgentSpineConfig
)
```

#### Methods

##### `execute_task` (Async)
Triggers the full pipeline orchestrator for a specific action.

```python
result = await spine.execute_task(
    task_id="unique_task_id",
    action="action_name",
    params={"foo": "bar"},
    hard_dedupe=True  # Optional, defaults to True
)
```
- **Returns**: `ActionResult` object.
- **Raises**: `PolicyViolation` if a policy blocks the action.

---

## Server API Reference

The AgentSpine server provides a RESTful API for interaction.

### Action Management

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/actions` | `POST` | Submit a new action request. |
| `/api/v1/actions` | `GET` | List recent action executions. |
| `/api/v1/actions/{id}` | `GET` | Get detailed state and timeline for an action. |
| `/api/v1/actions/{id}/replay` | `POST` | Re-run a historical action. |

### Governance & Approvals

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/approvals` | `GET` | List actions waiting for manual approval. |
| `/api/v1/approvals/{id}/resolve` | `POST` | Approve or reject a pending action. |
| `/api/v1/policies` | `GET` | List all active safety policies. |

### Observability

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/events` | `GET` | Stream the global event log. |
| `/api/v1/rewards` | `POST` | Record feedback/reward signals for an action. |
| `/health` | `GET` | Liveness and readiness check. |

---

## Data Models

### `ActionResult`
The object returned by SDK execution calls.

```python
class ActionResult(BaseModel):
    id: UUID
    status: ActionStatus # SUCCESS, FAILED, BLOCKED
    output: Optional[dict]
    error: Optional[str]
    metadata: dict
```
