# Purpose:
# This file defines the common interface (Protocol) and standard response format
# for all data connectors in the system.
#
# Why this file exists:
# The AI execution layer shouldn't care if data comes from Postgres, Mongo, or an API.
# By forcing every connector to return a "NormalizedResult", we decouple the AI logic
# from the physical data storage.
#
# In simple terms:
# This is the universal blueprint. It guarantees that no matter where we pull data from,
# it always gets handed back to the application in the exact same shape.

from typing import Protocol, Any, Dict, List
from pydantic import BaseModel

class ExecutionStep(BaseModel):
    dataset_id: str
    operation: str  # 'select', 'aggregate', 'filter'
    filters: Dict[str, Any]
    fields: List[str]

class NormalizedResult(BaseModel):
    source: str
    rows: List[Dict[str, Any]]
    columns: List[str]
    truncated: bool = False

class Connector(Protocol):
    async def fetch(self, plan: ExecutionStep) -> NormalizedResult:
        """
        Takes a structured execution step, executes it against the underlying
        data source, and returns a standardized result.
        """
        ...