"""FastAPI entry point for the AgentSpine standalone server."""

from fastapi import FastAPI
from agentspine import AgentSpine, FeatureFlags

app = FastAPI(title="AgentSpine Server")

# Initialize spine instance
spine = AgentSpine(
    workflow="default_server",
    features=FeatureFlags.full()
)

@app.on_event("startup")
async def startup():
    await spine._ensure_init()

@app.on_event("shutdown")
async def shutdown():
    await spine.close()

@app.get("/health")
async def health():
    return {"status": "ok"}
