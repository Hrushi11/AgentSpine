---
title: Plugins & Extensibility
description: Extending AgentSpine with custom adapters and policies.
---

AgentSpine is designed to be extensible without requiring you to fork the core SDK. You can hook into various lifecycle stages to add custom behavior.

## Extension Points

You can extend AgentSpine by implementing custom providers for:

- **Execution Adapters**: Define how actions are physically performed.
- **Policy Providers**: Add custom safety and governance logic.
- **Judge Providers**: Integrate custom AI or human-in-the-loop approval steps.
- **Notification Providers**: Send alerts when specific events occur.

## Design Philosophy

The core of AgentSpine remains **generic and unopinionated**. It manages the state and orchestration of actions, while provider-specific logic (e.g., how to send an email via SendGrid vs. Gmail) is abstracted into plugins.

## Implementation Status

> [!NOTE]
> The plugin architecture is currently being finalized. Basic policy and execution adapter extensibility is available now, with more specialized hooks coming in future releases.
