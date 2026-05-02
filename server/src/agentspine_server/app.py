"""FastAPI app factory for AgentSpine server mode."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from agentspine import AgentSpine, FeatureFlags
from agentspine_server.metrics import REQUEST_COUNT, REQUEST_LATENCY, render_metrics
from agentspine_server.routes.actions import router as actions_router
from agentspine_server.routes.approvals import router as approvals_router
from agentspine_server.routes.events import router as events_router
from agentspine_server.routes.health import router as health_router
from agentspine_server.routes.policies import router as policies_router
from agentspine_server.routes.rewards import router as rewards_router
from agentspine_server.routes.workflows import router as workflows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    spine = AgentSpine(
        workflow=os.environ.get("AGENTSPINE_SERVER_WORKFLOW", "default_server"),
        config_path=os.environ.get("AGENTSPINE_CONFIG_PATH"),
        features=FeatureFlags.full(),
        fail_mode=os.environ.get("AGENTSPINE_FAIL_MODE", "closed"),
    )
    await spine._ensure_init()
    app.state.spine = spine
    try:
        yield
    finally:
        await spine.close()


def create_app() -> FastAPI:
    app = FastAPI(title="AgentSpine Server", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def capture_metrics(request: Request, call_next):
        started = perf_counter()
        response = await call_next(request)
        elapsed = perf_counter() - started
        path = request.scope.get("route").path if request.scope.get("route") else request.url.path
        REQUEST_COUNT.labels(method=request.method, path=path, status=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method=request.method, path=path).observe(elapsed)
        return response

    app.include_router(health_router)
    app.include_router(actions_router, prefix="/api/v1")
    app.include_router(approvals_router, prefix="/api/v1")
    app.include_router(events_router, prefix="/api/v1")
    app.include_router(policies_router, prefix="/api/v1")
    app.include_router(rewards_router, prefix="/api/v1")
    app.include_router(workflows_router, prefix="/api/v1")

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(content=render_metrics(), media_type="text/plain; version=0.0.4")

    return app


app = create_app()
