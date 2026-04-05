import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Clave secreta para firmar los tokens
# En producción debe venir de una variable de entorno segura
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PROD")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Extractor de token: lee el header "Authorization: Bearer <token>" de cada request.
# tokenUrl es solo para que Swagger muestre el botón "Authorize" apuntando al login.
# Si el header no existe, FastAPI devuelve 401 automáticamente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_forbiden():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Permisos insuficientes",
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Calcula la expiración: usa expires_delta si se pasa, sino usa el valor por defecto
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    # Firma el payload con la clave secreta y devuelve el JWT como string
    token = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    # Verifica la firma y la expiración
    # Lanza excepción si el token es inválido
    payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return payload


# Dependencia de protección: se usa con Depends(get_current_user)
# en endpoints protegidos.
# Extrae y valida el token, devuelve el usuario o lanza 401.
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token=token)
        sub: Optional[str] = payload.get("sub")  # email del usuario
        username: Optional[str] = payload.get("username")
        if not sub or not username:
            raise credentials_exc

        return {"email": sub, "username": username}

    except jwt.ExpiredSignatureError:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Token Expirado",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        raise raise_expired_token()

    except jwt.InvalidTokenError:
        raise credentials_exc
