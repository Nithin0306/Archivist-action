from fastapi import FastAPI

app = FastAPI(title="Archivist")

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