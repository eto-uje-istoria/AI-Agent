from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_lenght=1)
    conversation_id: str | None = None


class ToolCallRecord(BaseModel):
    name: str
    input: dict[str, Any]


class Source(BaseModel):
    title: str | None = None
    url: str | None = None
    path: str | None = None


class ChatResponse(BaseModel):
    answer: str
    used_tools: list[ToolCallRecord] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"
