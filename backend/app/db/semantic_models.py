# Purpose:
# This file defines the SQLAlchemy ORM models for the Phase 2 semantic metadata layer,
# specifically mapping the dataset_registry and business_glossary tables.
#
# Why this file exists:
# By separating semantic models from the core RBAC models (models.py), we maintain
# cleaner domain boundaries. It allows the backend to perform pgvector similarity 
# searches using Python objects.
#
# In simple terms:
# This file tells our Python code what the dataset and glossary tables look like,
# including the special vector column for AI embeddings.

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from app.db.session import Base

class DatasetRegistry(Base):
    __tablename__ = "dataset_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"))
    connector_type = Column(Text, nullable=False)
    source_ref = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    allowed_operations = Column(ARRAY(Text), nullable=False)
    embedding = Column(Vector(384))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BusinessGlossary(Base):
    __tablename__ = "business_glossary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    term = Column(Text, nullable=False)
    definition = Column(Text, nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("dataset_registry.id"))
    field_mapping = Column(Text)
    embedding = Column(Vector(384))
    created_at = Column(DateTime(timezone=True), server_default=func.now())