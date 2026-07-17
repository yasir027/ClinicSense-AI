# Purpose:
# This file defines the audit_log database model for tracking sensitive system actions.
#
# Why this file exists:
# The platform must keep a record of important actions such as login, query,
# export, and permission changes. Keeping this in its own model makes audit
# logging easy to reuse later.

from sqlalchemy import Column, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type = Column(Text, nullable=False)
    category = Column(Text)
    module = Column(Text)
    detail = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())