# Purpose:
# This file exposes the main conversational API endpoint for the frontend.
#
# Why this file exists:
# The user just wants to send a text question and get an answer. This file orchestrates 
# all our internal systems (vector search, AI planning, database execution) to make that happen.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Any, Dict

from app.db.session import get_db
from app.core.deps import get_current_user
from app.semantic.search import find_relevant_datasets
from app.ai.groq_client import GroqService
from app.execution.executor import execute_plan

router = APIRouter(prefix="/chat", tags=["Chat & Execution"])
ai_service = GroqService()

# 1. Define what the frontend will send and receive
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    needs_clarification: bool = False
    data_sources: List[str] = []
    raw_data: List[Dict[str, Any]] = []

@router.post("/", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Security: Must be logged in
):
    try:
        # Step 1: Semantic Search (Phase 2)
        # Find which datasets match the user's question.
        # (In a full app, you filter this list strictly by current_user's RBAC modules here)
        matched_datasets = find_relevant_datasets(db, request.message)
        
        # Format for the AI
        allowed_datasets_context = [
            {
                "id": str(ds.id), 
                "description": ds.description, 
                "allowed_operations": ds.allowed_operations
            } for ds in matched_datasets
        ]

        # Step 2: AI Planning (Phase 4)
        # Ask Groq to build a strict JSON plan using only those datasets
        plan = await ai_service.plan_query(request.message, allowed_datasets_context)

        # Step 3: Check for Clarification (Phase 4 & 5)
        if plan.needs_clarification:
            return ChatResponse(
                answer=plan.clarification_question or "Could you please clarify your request?",
                needs_clarification=True
            )

        # Step 4: Secure Execution (Phase 5)
        # The executor validates the plan and safely pulls the data
        execution_results = await execute_plan(db, plan, current_user)
        
        # Step 5: Draft Narrative (Phase 4)
        # Turn the raw database rows into a polite human sentence
        raw_results_dict = [res.model_dump() for res in execution_results]
        narrative = await ai_service.draft_narrative(request.message, raw_results_dict)

        # Step 6: Return the final package to the user
        return ChatResponse(
            answer=narrative,
            data_sources=[step.dataset_id for step in plan.steps],
            raw_data=raw_results_dict
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))