import os
from contextlib import asynccontextmanager

from api.v1.auth.router import router as auth_router
from api.v1.posts.router import router as post_router
from api.v1.uploads.router import MEDIA_DIR
from api.v1.uploads.router import router as uploads_router
from core.db import DATABASE_URL, Base, engine, logger
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db_type = "PostgreSQL" if DATABASE_URL.startswith("postgresql") else "SQLite"
    db_name = DATABASE_URL.rsplit("/", 1)[-1]
    logger.info(
        "\n"
        "  ┌─────────────────────────────────────────┐\n"
        "  │         Base de datos conectada          │\n"
        "  ├─────────────────────────────────────────┤\n"
        "  │  Motor  : %s\n"
        "  │  Nombre : %s\n"
        "  └─────────────────────────────────────────┘",
        db_type,
        db_name,
    )
    yield


# ============== APP de FastAPI =======================
def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog", lifespan=lifespan)

    app.include_router(router=auth_router, prefix="/api/v1")
    app.include_router(router=post_router)
    app.include_router(router=uploads_router)

    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app


app = create_app()
