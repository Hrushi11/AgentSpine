---
title: Pipeline Model
description: How AgentSpine orchestrates action validation and execution.
---

The **Pipeline Orchestrator** is the core component responsible for taking an action request and driving it to completion while ensuring all safety checks are satisfied.

## Pipeline Phases

Every action request moves through a series of discrete phases:

### 1. Pre-Execution (Validation)
Before any action is taken, the orchestrator performs:
- **Registration**: Assigning a unique UUID to the execution record.
- **Deduplication**: Checking if this exact action has been performed recently.
- **Policy Check**: Running all registered "Pre-execution" policies.

### 2. Execution (The Action)
The orchestrator triggers the **Execution Adapter**. This is the step where the "work" happens (e.g., calling an API, running a script).

### 3. Post-Execution (Verification)
After the action completes, the orchestrator:
- **Logs Results**: Captures the output or error message.
- **Post-Policy Check**: Runs any "Post-execution" policies (e.g., verifying the email was actually delivered).
- **Finalizes State**: Marks the execution as `SUCCESS` or `FAILED`.

## Handling Failures

AgentSpine provides robust error handling within the pipeline:

- **Idempotency Errors**: If an action is blocked by deduplication, the orchestrator returns the result of the *original* execution.
- **Policy Violations**: If a policy fails, the action is blocked, and the reason is logged to the database.
- **Execution Failures**: If the external adapter crashes, the orchestrator captures the stack trace and updates the execution status.

## Example: Custom Pipeline Policy

You can extend the pipeline by registering custom policies:

```python
from agentspine.policies import BasePolicy

class MySafetyPolicy(BasePolicy):
    async def evaluate(self, execution_context):
        # Prevent actions after 10 PM
        if current_hour() > 22:
            return self.block("No actions allowed at night!")
        return self.approve()
```
