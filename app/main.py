from fastapi import FastAPI
from app.api.webhooks import router as webhooks_router

app = FastAPI(
    title="Archivist",
    description="Autonomous Architecture Governance Engine")

@app.get("/")
async def root():
    return {
        "message": "Service is running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }

app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])