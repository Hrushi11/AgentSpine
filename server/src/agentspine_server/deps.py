"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from agentspine import AgentSpine


def get_spine(request: Request) -> AgentSpine:
    return request.app.state.spine
