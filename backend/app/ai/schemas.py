# Purpose:
# This file defines the strict JSON structure we demand from the AI.
#
# Why this file exists:
# We cannot run raw text against a database. We need the AI to output exactly 
# which dataset it wants, what filters to apply, and what fields to return.
#
# In simple terms:
# This is a fill-in-the-blank form we hand to the AI. It forces the AI to give us
# a machine-readable plan instead of a conversational answer.

from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Optional

class ExecutionStep(BaseModel):
    dataset_id: str
    operation: Literal['select', 'aggregate', 'filter']
    filters: Dict[str, Any]
    fields: List[str]

class QueryPlan(BaseModel):
    intent_summary: str
    categories: List[str]
    steps: List[ExecutionStep]
    needs_clarification: bool
    clarification_question: Optional[str] = None