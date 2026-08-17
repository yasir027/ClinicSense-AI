# Purpose:
# This file implements the REST API connector adapter.
#
# Why this file exists:
# Not all data lives in our own databases. Insurance claims often live in external
# vendor systems. This connector standardizes how we ask those external systems for
# data securely over the web.

import os
import httpx
from typing import Any, Dict
from app.connectors.base import Connector, ExecutionStep, NormalizedResult

class RestAPIConnector(Connector):
    def __init__(self, source_name: str = "rest_api"):
        self.source_name = source_name
        # Fetch the URL and secure token from environment variables
        self.api_base_url = os.getenv("INSURANCE_API_URL", "http://localhost:8000/mock-api")
        self.api_key = os.getenv("INSURANCE_API_KEY", "mock-bearer-token")

    async def fetch(self, plan: ExecutionStep) -> NormalizedResult:
        # 1. Setup secure headers
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # 2. Map AI filters to URL parameters (e.g., ?status=pending)
        params = plan.filters if plan.filters else {}
        
        # 3. Define the endpoint (Mocked for MVP)
        endpoint = f"{self.api_base_url}/claims"

        # 4. Open an async client with a strict 10-second timeout
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Make the GET request
                response = await client.get(endpoint, headers=headers, params=params)
                response.raise_for_status() # Throws an error if the server says 404 or 500
                
                data = response.json()
                
                # Ensure data is a list for consistent processing
                if isinstance(data, dict):
                    data = [data]

                rows = []
                columns_set = set()

                # 5. Filter and format the data
                for item in data:
                    if plan.fields:
                        # Keep only the fields the AI asked for
                        filtered_item = {k: v for k, v in item.items() if k in plan.fields}
                    else:
                        filtered_item = item
                        
                    rows.append(filtered_item)
                    columns_set.update(filtered_item.keys())
                    
                # 6. Return the standardized result
                return NormalizedResult(
                    source=self.source_name,
                    rows=rows,
                    columns=list(columns_set)
                )
                
            except httpx.HTTPError as e:
                # If the external server crashes or times out, we catch it gracefully
                print(f"Network error when calling external API: {e}")
                return NormalizedResult(source=self.source_name, rows=[], columns=[])