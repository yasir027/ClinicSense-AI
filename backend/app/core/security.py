# Purpose:
# This file contains reusable security helpers such as password hashing,
# password verification, and JWT token creation.
#
# Why this file exists:
# Authentication logic should not be scattered across route files.
# By keeping hashing and token functions here, the login flow stays clean,
# reusable, and easier to audit or upgrade later.



from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)