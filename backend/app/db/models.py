# Purpose:
# This file defines the SQLAlchemy ORM models that map Python classes
# to PostgreSQL tables such as users, roles, categories, modules, and role_permissions.
#
# Why this file exists:
# The backend needs a structured Python representation of the database schema
# so code can query and manipulate records without writing raw SQL everywhere.
#
# In simple terms:
# This file describes what the database tables look like in Python language.
# Each class here represents one table in PostgreSQL.

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role")

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)

class Module(Base):
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    name = Column(Text, nullable=False)

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), primary_key=True)