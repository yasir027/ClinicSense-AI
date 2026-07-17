# Purpose:
# This file contains protected test routes used to verify that login and RBAC
# are working before more advanced business routes are added.
#
# Why this file exists:
# It gives us a safe endpoint to confirm that the backend can correctly allow
# an authorized user and block an unauthorized user.
#
# In simple terms:
# This file is just a permission test endpoint.

from fastapi import APIRouter, Depends
from app.core.rbac import require_module

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/billing")
def billing_check(user=Depends(require_module("Billing"))):
    return {
        "message": "You are authorized for the Billing module",
        "user_email": user.email,
    }