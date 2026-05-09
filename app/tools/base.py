from typing import Any

from pydantic import BaseModel, Field

from app.schemas import Source


class ToolExecutionResult(BaseModel):
    content: dict[str, Any]
    sources: list[Source] = Field(default_factory=list)
