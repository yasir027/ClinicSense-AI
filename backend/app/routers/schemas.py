# Purpose:
# This file contains request and response schemas used by route handlers,
# especially authentication routes in the current phase.
#
# Why this file exists:
# Route input and output should be structured and validated instead of using
# loose dictionaries everywhere. Keeping schemas separate makes the API cleaner,
# easier to test, and easier to expand later.
#
# In simple terms:
# This file defines the shape of the data the API expects and returns.

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"