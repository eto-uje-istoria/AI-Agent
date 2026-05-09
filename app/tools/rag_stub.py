from typing import Any

from app.tools.base import ToolExecutionResult


async def rag_retrieve_stub(query: str) -> ToolExecutionResult:
    return ToolExecutionResult(
        content={
            "query": query,
            "status": "not_implemented",
            "message": "RAG retrieval is not implemented yet. It will be added in SCRUM-23.",
            "documents": [],
        }
    )


RAG_RETRIEVE_STUB_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "rag_retrieve_stub",
        "description": "Temporary stub for future RAG retrieval. Use it when the user asks to search internal knowledge base or corporate documentation.",
        "parametrs": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "User query for future RAG retrieval.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
