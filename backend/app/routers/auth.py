# Purpose:
# This file contains authentication-related API routes such as login.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.core.security import verify_password, create_access_token
from app.routers.schemas import LoginRequest, TokenResponse
from app.audit.writer import write_audit_log

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {
            "sub": user.email,
            "role_id": str(user.role_id) if user.role_id else None,
        }
    )

    write_audit_log(
        db=db,
        user_id=user.id,
        event_type="login",
        detail={"email": user.email},
    )

    return TokenResponse(access_token=token)