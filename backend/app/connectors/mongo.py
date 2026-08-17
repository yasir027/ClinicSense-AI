# Purpose:
# This file implements the MongoDB connector adapter.
#
# Why this file exists:
# It connects to MongoDB to query unstructured data like doctor notes and treatment logs.
# Crucially, it translates the AI's ExecutionStep into safe PyMongo queries, explicitly 
# validating and sanitizing filters to prevent NoSQL injections (like $where).
#
# In simple terms:
# This is the translator that turns the AI's request into a MongoDB search, 
# designed for document-based medical records, while ensuring the AI can't run 
# malicious database commands.

import os
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.connectors.base import Connector, ExecutionStep, NormalizedResult

class MongoConnector(Connector):
    def __init__(self, source_name: str = "mongo"):
        self.source_name = source_name
        # In a real app, this should be loaded from app.core.config (settings.py)
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client.clinicsense

    async def fetch(self, plan: ExecutionStep) -> NormalizedResult:
        # MVP Safety Check: Enforce allowed operations
        if plan.operation not in ["select", "filter"]:
            raise ValueError(f"Operation {plan.operation} not supported by MongoConnector")

        # Resolve the collection (Placeholder mapping for MVP)
        # You will map plan.dataset_id to the actual collection name dynamically later.
        collection_name = "doctor_notes" 
        collection = self.db[collection_name]

        # Construct safe filters
        safe_filters = {}
        if plan.filters:
            for key, value in plan.filters.items():
                # Security: Prevent NoSQL injection via $where, $expr, or eval
                if key.startswith("$") or (isinstance(value, dict) and any(k.startswith("$") for k in value.keys())):
                    # For MVP, we strip out nested operators or throw an error.
                    # We only allow basic equality filters here to maintain strict safety.
                    continue
                
                # Handle ObjectId conversion if querying by _id
                if key == "_id" and isinstance(value, str):
                    safe_filters[key] = ObjectId(value)
                else:
                    safe_filters[key] = value

        # Projection (fields to return)
        projection = None
        if plan.fields:
            projection = {field: 1 for field in plan.fields}
            # Explicitly exclude _id if it wasn't requested
            if "_id" not in plan.fields:
                projection["_id"] = 0 

        # Execute query asynchronously
        cursor = collection.find(safe_filters, projection)
        
        rows = []
        columns_set = set()
        
        async for document in cursor:
            # Convert ObjectId to string for clean JSON serialization
            if "_id" in document:
                document["_id"] = str(document["_id"])
            
            rows.append(document)
            columns_set.update(document.keys())

        return NormalizedResult(
            source=self.source_name,
            rows=rows,
            columns=list(columns_set)
        )