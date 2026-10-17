from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# Five ops-center sample users (password: OpsCenter2026!)
OPS_USERS: dict[str, dict[str, str]] = {
    "ops.alice": {
        "username": "ops.alice",
        "full_name": "Alice Chen",
        "role": "lead",
        "password_hash": pwd_context.hash("OpsCenter2026!"),
    },
    "ops.bob": {
        "username": "ops.bob",
        "full_name": "Bob Martinez",
        "role": "engineer",
        "password_hash": pwd_context.hash("OpsCenter2026!"),
    },
    "ops.carol": {
        "username": "ops.carol",
        "full_name": "Carol Okonkwo",
        "role": "engineer",
        "password_hash": pwd_context.hash("OpsCenter2026!"),
    },
    "ops.dave": {
        "username": "ops.dave",
        "full_name": "Dave Patel",
        "role": "engineer",
        "password_hash": pwd_context.hash("OpsCenter2026!"),
    },
    "ops.eve": {
        "username": "ops.eve",
        "full_name": "Eve Nguyen",
        "role": "oncall",
        "password_hash": pwd_context.hash("OpsCenter2026!"),
    },
}


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(username: str, password: str) -> dict[str, str] | None:
    user = OPS_USERS.get(username)
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
    }


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, str]:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if not username or username not in OPS_USERS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    u = OPS_USERS[username]
    return {"username": u["username"], "full_name": u["full_name"], "role": u["role"]}
