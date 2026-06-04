from pydantic import BaseModel, Field
from typing import Optional, Literal, List

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="The user query to be processed.")
    session_id: Optional[str] = Field(None, description="Optional UUID to identify the chat session.")
    selected_funds: Optional[List[str]] = Field(None, description="Optional list of fund IDs to restrict the RAG context.")


class Citation(BaseModel):
    label: str = Field(..., description="Muted/friendly description of the source fund name.")
    url: str = Field(..., description="Link to the official INDMoney page.")

class ChatResponse(BaseModel):
    status: Literal["success", "refused"] = Field(..., description="Status of query validation.")
    type: Literal["factual", "advisory", "pii", "comparison", "out_of_scope", "greeting"] = Field(
        ..., description="The classified category of the query."
    )
    answer: str = Field(..., description="The objective answer or refusal response text.")
    citation: Optional[Citation] = Field(None, description="Link citation (only for successful factual queries).")
    last_updated: Optional[str] = Field(None, description="The ISO scrape timestamp (only for successful factual queries).")
