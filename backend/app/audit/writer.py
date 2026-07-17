# Purpose:
# This file contains helper functions for writing audit events to the database.
#
# Why this file exists:
# Audit logging should be done in one consistent way across login, queries,
# exports, and emails so every important action is recorded uniformly.
#
# In simple terms:
# This file is the code that writes activity records into the audit log table.

from sqlalchemy.orm import Session

from app.db.audit_model import AuditLog


def write_audit_log(db: Session, user_id, event_type: str, category=None, module=None, detail=None):
    entry = AuditLog(
        user_id=user_id,
        event_type=event_type,
        category=category,
        module=module,
        detail=detail,
    )
    db.add(entry)
    db.commit()