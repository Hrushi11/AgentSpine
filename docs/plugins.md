# Plugins

AgentSpine is intended to be extensible without forking the SDK core.

## Extension Points

- Execution adapters
- Policy providers
- Judge providers
- Notification providers
- Credential backends
- Event bus adapters

## Principle

Core AgentSpine should stay generic.

- It emits normalized action requests and execution signals.
- It records policy, approval, risk, and outcome metadata.
- External services may implement provider-specific behavior.

## Current State

The plugin surface is planned in the technical design doc and will be implemented incrementally.
This document exists so the public docs tree is coherent while the implementation is still underway.
