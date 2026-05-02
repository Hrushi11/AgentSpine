"""Prometheus metrics for server mode."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "agentspine_http_requests_total",
    "Total HTTP requests received by AgentSpine server",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "agentspine_http_request_duration_seconds",
    "HTTP request latency for AgentSpine server",
    ["method", "path"],
)
ACTION_SUBMISSIONS = Counter(
    "agentspine_action_submissions_total",
    "Total action submissions grouped by final status",
    ["status"],
)
PENDING_APPROVALS = Gauge(
    "agentspine_pending_approvals",
    "Current number of pending approvals returned by the approval inbox query",
)


def render_metrics() -> bytes:
    return generate_latest()
