# Purpose:
# This file will hold reusable RBAC (role-based access control) checks,
# especially module/category permission enforcement for protected routes.
#
# Why this file exists:
# Permission logic should be centralized, not rewritten in every route.
# The project guide expects one shared dependency that can block unauthorized access
# before any AI query, connector call, export action, or sensitive operation runs.

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.db.models import RolePermission, Module


def user_has_module_permission(user, module_name: str, db: Session) -> bool:
    if not user.role_id:
        return False

    module = db.query(Module).filter(Module.name == module_name).first()
    if not module:
        return False

    permission = (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == user.role_id,
            RolePermission.module_id == module.id,
        )
        .first()
    )

    return permission is not None


def require_module(module_name: str):
    def checker(
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not user_has_module_permission(user, module_name, db):
            raise HTTPException(status_code=403, detail="Not authorized for this module")
        return user

    return checker