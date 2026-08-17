# Purpose:
# This file defines the Pydantic schemas for validating and serializing semantic data.
#
# Why this file exists:
# FastAPI relies on Pydantic to convert SQLAlchemy model instances into JSON responses.
# It also ensures we only expose necessary fields (e.g., filtering out the embedding vectors).
#
# In simple terms:
# This file shapes the JSON output so that when someone searches for a dataset, 
# they get a clean, predictable response back without raw database clutter.

from pydantic import BaseModel
from typing import List
from uuid import UUID

class DatasetResult(BaseModel):
    id: UUID
    connector_type: str
    source_ref: str
    description: str
    allowed_operations: List[str]

    class Config:
        from_attributes = True

class SemanticSearchResponse(BaseModel):
    query: str
    matched_datasets: List[DatasetResult]