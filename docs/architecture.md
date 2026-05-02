# Architecture

AgentSpine is a control plane for agent actions, not a provider-specific workflow engine.

## Core Runtime Model

```text
Agent
  -> AgentSpine SDK
  -> safety and control pipeline
  -> execution adapter boundary
  -> external executor or downstream system
```

## Main Subsystems

- Policy engine
- Hard and semantic dedupe
- Risk scoring
- Lock manager
- Knowledge graph
- Event timeline
- Reward logging
- Judiciary and approval flow
- Generic execution adapters

## Runtime Modes

- Embedded SDK mode
  - direct Postgres and Redis access
  - lowest latency path
- Optional server mode
  - HTTP API for untrusted or multi-language clients
  - dashboard and webhook entry points

## Design Boundary

The SDK should not assume Gmail, Salesforce, HubSpot, or any other single provider.
Provider-specific execution belongs behind a generic adapter contract or in external executor services.
