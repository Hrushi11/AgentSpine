---
name: agentspine-sdk
description: Guide for using the AgentSpine Python SDK to add control planes, policies, distributed locks, and semantic deduplication to AI agents. Use this when writing or modifying AI agents that use the agentspine library.
---

# AgentSpine SDK Skill

You are an expert in integrating the `agentspine` Python SDK into AI applications. AgentSpine is an embedded control plane that sits between an AI agent and the tools it uses.

## Core Concepts

1. **Initialization**:
   The SDK is initialized via the `AgentSpine` client, which requires a workflow name and optional feature flags. By default, it runs in `full` mode.

   ```python
   from agentspine import AgentSpine, FeatureFlags

   # Full mode (default)
   spine = AgentSpine(workflow="ai_sdr")
   
   # Minimal mode (only policy & events, lowest overhead)
   spine = AgentSpine(workflow="ai_sdr", features=FeatureFlags.minimal())
   ```

2. **Action Requests**:
   Agents do not execute tools directly. Instead, they request actions through AgentSpine, which evaluates policies, deduplication, locks, and risk before executing.

   ```python
   result = await spine.request_action(
       agent="outreach_agent",
       action_type="email.send",
       payload={"to": "user@example.com", "body": "Hello"},
       idempotency_key="unique_key_123", # For hard deduplication
       dry_run=False
   )

   if result.status == "executed":
       print("Success:", result.result)
   elif result.status == "denied":
       print("Blocked by policy/rate limit:", result.reason)
   elif result.status == "blocked":
       print("Duplicate action blocked:", result.reason)
   ```

3. **Feature Flags**:
   AgentSpine is highly modular. If an infrastructure piece (like Redis for rate limiting, or pgvector for semantic dedupe) is unavailable, ensure you configure the `AgentSpine` instance with a `FeatureFlags` object that disables those features.

## Rules for Agents

- **Always pass an `idempotency_key`** when requesting side-effect actions (like sending emails or making payments) to utilize the Hard Deduplication step.
- **Handle `ActionResult` statuses properly**. Do not assume a requested action was executed. Check `result.status` (which can be `executed`, `denied`, `blocked`, `pending_approval`, etc.).
- **Async First**: AgentSpine relies on `asyncio`. Ensure you `await` the client methods. If you are in a synchronous context, you can use `spine.request_action_sync()`.
- **Cleanup**: Always gracefully shut down the connection pools using `await spine.close()` when the application exits.

## Database & Infrastructure
AgentSpine relies on PostgreSQL (with `pgvector` for semantic deduplication and recursive CTEs for the Knowledge Graph) and optionally Redis (for distributed locks, rate limiting, and circuit breakers). 
