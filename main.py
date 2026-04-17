from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.movies.router import router as movies_router
from src.reactions.router import router as reactions_router
from src.favorites.router import router as favorites_router
from src.movies import models as movies_models  # noqa
from src.reactions import models as reactions_models  # noqa
from src.favorites import models as favorites_models  # noqa
from src.core.database import engine, Base, AsyncSessionLocal
from src.core.seed import seed_user_groups



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_user_groups(db)
    yield


app = FastAPI(
    title="Online Cinema API",
    description="API for Online Cinema Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(reactions_router)
app.include_router(favorites_router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Online Cinema API is running"}
