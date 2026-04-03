from contextlib import asynccontextmanager

from api.v1.posts.router import router as post_router
from core.db import DATABASE_URL, Base, engine, logger
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
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

    app.include_router(router=post_router)

    return app


app = create_app()
