import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ============== Config Database Connect =======================
load_dotenv()


# Lee la URL de conexión, crea el engine de SQLAlchemy y la fábrica de sesiones
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
logger = logging.getLogger("uvicorn.error")

# Argumentos extra para SQLite: evita el error de "same thread" en entornos async
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Motor de conexión a la base de datos, con echo opcional para debug
engine = create_engine(
    DATABASE_URL, echo=os.getenv("DB_ECHO", "false").lower() == "true", **engine_kwargs
)

# Fábrica de sesiones reutilizable vinculada al engine
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


# Clase base de la que heredan todos los modelos ORM
class Base(DeclarativeBase):
    pass


# Dependencia de FastAPI que provee una sesión de DB por request y ciclo de vida
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
