from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from core.config import Settings
from core.db import DbSession
from core.enums import Role
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)

invalid_token_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token inválido",
    headers={"WWW-Authenticate": "Bearer"},
)


forbidden_exc = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Permisos insuficientes",
)


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token(token: str) -> dict:
    # Verifica la firma y la expiración
    # Lanza excepción si el token es inválido
    payload = jwt.decode(
        jwt=token, key=Settings.JWT_SECRET, algorithms=[Settings.JWT_ALG]
    )
    return payload


def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=minutes or Settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": sub, "exp": expire}, Settings.JWT_SECRET, algorithm=Settings.JWT_ALG
    )


async def get_current_user(db: DbSession, token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token=token)
    except jwt.ExpiredSignatureError:
        raise raise_expired_token()
    except jwt.InvalidTokenError:
        raise credentials_exc
    except jwt.PyJWTError:
        raise invalid_token_exc

    sub: Optional[str] = payload.get("sub")
    if not sub:
        raise credentials_exc

    user = await db.get(User, int(sub))
    if not user or not user.is_active:
        raise credentials_exc

    return user


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hash: str) -> bool:
    return password_hash.verify(plain, hash=hash)


def require_role(min_role: Role):
    order = {Role.user: 0, Role.editor: 1, Role.admin: 2}

    async def check(current_user: User = Depends(get_current_user)):
        if order[current_user.role] < order[min_role]:
            raise forbidden_exc
        return current_user

    return check


require_user = require_role(Role.user)
require_editor = require_role(Role.editor)
require_admin = require_role(Role.admin)
