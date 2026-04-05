import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ============== Config Database Connect =======================
load_dotenv()


# Lee la URL de conexión, crea el engine de SQLAlchemy y la fábrica de sesiones
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./blog.db")
logger = logging.getLogger("uvicorn.error")

# Motor de conexión async a la base de datos, con echo opcional para debug
engine = create_async_engine(
    DATABASE_URL, echo=os.getenv("DB_ECHO", "false").lower() == "true"
)

# Fábrica de sesiones async reutilizable vinculada al engine
SessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=AsyncSession
)


# Clase base de la que heredan todos los modelos ORM
class Base(DeclarativeBase):
    pass


# Dependencia de FastAPI que provee una sesión async de DB por request y ciclo de vida
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise


DbSession = Annotated[AsyncSession, Depends(get_db)]
