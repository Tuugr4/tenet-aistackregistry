from fastapi import FastAPI

from app.routers import all_routers

app = FastAPI(title="tenet-aistackregistry", version="0.1.0")

for router in all_routers:
    app.include_router(router, prefix="/api/v1")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
