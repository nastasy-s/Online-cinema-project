from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Online Cinema API",
    description="API for Online Cinema Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Online Cinema API is running"}
