# Purpose:
# This file provides a centralized factory to resolve connector instances
# based on their connector_type string.
#
# Why this file exists:
# The execution engine shouldn't manually instantiate different connector classes.
# It simply looks up the dataset's connector_type from dataset_registry and asks
# this factory for the right connector adapter.
#
# In simple terms:
# This is the connector switchboard. Give it a type like "postgres" or "mongo",
# and it hands back the right tool for the job.

from typing import Dict
from app.connectors.base import Connector
from app.connectors.postgres import PostgresConnector
from app.connectors.mongo import MongoConnector
from app.connectors.rest_api import RestAPIConnector
from app.connectors.spreadsheet import SpreadsheetConnector
from app.connectors.pdf_ocr import PdfOcrConnector

_REGISTRY: Dict[str, Connector] = {
    "postgres": PostgresConnector(),
    "mongo": MongoConnector(),
    "rest_api": RestAPIConnector(),
    "spreadsheet": SpreadsheetConnector(),
    "file": SpreadsheetConnector(),
    "pdf": PdfOcrConnector(),
    "pdf_ocr": PdfOcrConnector()
}

def get_connector(connector_type: str) -> Connector:
    connector = _REGISTRY.get(connector_type.lower())
    if not connector:
        raise ValueError(f"Unknown connector type: '{connector_type}'. Registered: {list(_REGISTRY.keys())}")
    return connector