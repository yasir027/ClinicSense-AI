# Purpose:
# This file handles all communication with the Groq API.
#
# Why this file exists:
# We need an isolated place to format our prompts, inject the allowed datasets,
# and parse the AI's response back into our Pydantic objects.
#
# In simple terms:
# This is the translator. It takes the user's question, attaches a list of 
# files they are allowed to see, sends it to the AI, and translates the AI's 
# response back into a strict plan.

import os
import json
from groq import AsyncGroq
from app.ai.schemas import QueryPlan

class GroqService:
    def __init__(self):
        # The SDK automatically looks for the GROQ_API_KEY environment variable
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        # Using a fast model capable of strict JSON output
        self.model = "llama3-70b-8192" 

    def _build_planning_prompt(self, user_message: str, allowed_datasets: list[dict], history: list[dict]) -> list[dict]:
        """Constructs the system prompt with role-scoped datasets."""
        
        # We inject ONLY the datasets this specific user is allowed to see
        dataset_context = json.dumps(allowed_datasets, indent=2)
        
        system_prompt = f"""
        You are an enterprise data routing AI. Your job is to translate user questions into a structured QueryPlan.
        You may ONLY query the following datasets:
        {dataset_context}
        
        If the user asks a question that cannot be answered by these datasets, set needs_clarification to true.
        Do NOT guess field names. Only use fields explicitly mentioned in the dataset definitions.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        return messages

    async def plan_query(self, user_message: str, allowed_datasets: list[dict], history: list[dict] = None) -> QueryPlan:
        if history is None:
            history = []
            
        messages = self._build_planning_prompt(user_message, allowed_datasets, history)
        
        # Call Groq with strict JSON schema constraints
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": QueryPlan.model_json_schema()},
            temperature=0.0 # Zero creativity, maximum precision
        )
        
        raw_json = response.choices[0].message.content
        
        # Pydantic re-validates the AI's output — we never trust the model blindly
        return QueryPlan.model_validate_json(raw_json)

    async def draft_narrative(self, user_message: str, execution_results: list[dict]) -> str:
        """
        Called in Phase 5 after data is fetched.
        Turns raw database rows into a short, human-readable answer.
        """
        data_context = json.dumps(execution_results, indent=2)
        
        system_prompt = f"""
        You are a helpful medical data assistant. Answer the user's question based strictly on the provided data.
        Data: {data_context}
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content