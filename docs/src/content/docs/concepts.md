---
title: Core Concepts
description: Understanding the fundamental building blocks of AgentSpine.
---

AgentSpine is designed as a **decoupled control plane** for AI agents. Unlike traditional agent frameworks, AgentSpine does not dictate how you build your agent (it works with LangChain, CrewAI, Autogen, or custom code); instead, it manages the **governance, safety, and reliability** of the agent's actions.

## The Agent Runtime Loop

In a production environment, an agent's lifecycle follows this flow when integrated with AgentSpine:

1. **Intention**: The agent decides to perform an action (e.g., "Send an email").
2. **Consultation**: The agent calls the AgentSpine SDK to validate the action.
3. **Orchestration**: AgentSpine runs the action through the **Policy Pipeline**.
4. **Enforcement**: Policies (Deduplication, Risk Scoring, Guardrails) approve or block the action.
5. **Execution**: If approved, the action is dispatched to an executor.
6. **Persistence**: The result is logged to the **Event Timeline** for auditing and self-improvement.

## Key Subsystems

### 1. Policy Engine
The heart of AgentSpine. It evaluates every requested action against a set of rules. Policies can be:
- **Synchronous**: Immediate pass/fail based on hard rules.
- **Asynchronous**: Triggering external approvals or complex analysis.

### 2. Idempotency & Deduplication
Prevents agents from repeating the same action unintentionally (e.g., sending the same email twice).
- **Hard Dedupe**: Exact match on action and parameters (powered by Redis).
- **Semantic Dedupe**: (Coming Soon) Detects conceptually identical actions.

### 3. Execution Adapters
AgentSpine provides a generic boundary for executing actions. This allows you to swap out implementations (e.g., from a local function to a remote webhook) without changing the agent's core logic.

### 4. Event Timeline
A chronological record of every decision, action, and result. This timeline is the foundation for:
- **Audit Logs**: Why did the agent do this?
- **Replay**: Debugging complex agent failures.
- **Reward Logging**: Providing feedback to the agent's underlying model for training.

---

## Deployment Modes

AgentSpine supports two primary integration patterns:

### Embedded SDK (Recommended)
The SDK runs inside your Python process and connects directly to your databases. This provides the lowest latency and is ideal for Python-based agent stacks.

### Centralized Server
A standalone FastAPI server that exposes an HTTP API. This allows non-Python agents to interact with the control plane and enables the centralized Dashboard.
