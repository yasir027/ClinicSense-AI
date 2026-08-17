# Purpose:
# This file implements the Excel/CSV file connector adapter.
#
# Why this file exists:
# A lot of hospital data, like pharmacy inventory or manual logs, lives in 
# spreadsheets rather than databases. This connector treats flat files exactly 
# like a database table, allowing the AI to query them seamlessly.

import os
import asyncio
import pandas as pd
from typing import Any, Dict
from app.connectors.base import Connector, ExecutionStep, NormalizedResult

class SpreadsheetConnector(Connector):
    def __init__(self, source_name: str = "spreadsheet"):
        self.source_name = source_name
        # Secure directory where files are allowed to be read from
        self.base_dir = os.getenv("SPREADSHEET_DIR", "./data/files")

    def _execute_sync(self, plan: ExecutionStep) -> NormalizedResult:
        # 1. Resolve the file path securely
        # For MVP, we assume dataset_id is the filename (e.g., 'pharmacy_inventory.xlsx')
        file_path = os.path.join(self.base_dir, f"{plan.dataset_id}")

        # Basic security check to prevent directory traversal attacks
        if not os.path.abspath(file_path).startswith(os.path.abspath(self.base_dir)):
            raise PermissionError("Access to this file path is forbidden.")

        if not os.path.exists(file_path):
            return NormalizedResult(source=self.source_name, rows=[], columns=[])

        # 2. Load the data into a Pandas DataFrame
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError("Unsupported file format. Must be .csv or .xlsx")

        # 3. Apply Filters
        if plan.filters:
            for col, val in plan.filters.items():
                if col in df.columns:
                    # Pandas boolean indexing
                    df = df[df[col] == val]

        # 4. Apply Column Selection (Fields)
        if plan.fields:
            # Ensure we only ask for columns that actually exist in the file
            valid_fields = [f for f in plan.fields if f in df.columns]
            if valid_fields:
                df = df[valid_fields]

        # 5. Clean and format the data
        # JSON cannot handle NaN (Not a Number) values, so we replace them with None (Null)
        df = df.where(pd.notnull(df), None)
        
        # Convert DataFrame to a list of dictionaries
        rows = df.to_dict(orient="records")

        return NormalizedResult(
            source=self.source_name,
            rows=rows,
            columns=list(df.columns)
        )

    async def fetch(self, plan: ExecutionStep) -> NormalizedResult:
        # Wrap the synchronous Pandas operations in a background thread
        # to satisfy the async connector contract without freezing the server
        return await asyncio.to_thread(self._execute_sync, plan)