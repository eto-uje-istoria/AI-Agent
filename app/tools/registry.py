import json
from collections.abc import Awaitable, Callable
from typing import Any

from app.schemas import Source, ToolCallRecord
from app.tools.base import ToolExecutionResult
from app.tools.calculator import CALCULATOR_SCHEMA, calculator
from app.tools.file_reader import FILE_READER_SCHEMA, file_reader
from app.tools.rag_stub import RAG_RETRIEVE_STUB_SCHEMA, rag_retrieve_stub
from app.tools.web_search import WEB_SEARCH_SCHEMA, web_search


ToolFunction = Callable[..., Awaitable[ToolExecutionResult]]

TOOL_SCHEMAS: list[dict[str, Any]] = [
    CALCULATOR_SCHEMA,
    FILE_READER_SCHEMA,
    WEB_SEARCH_SCHEMA,
    RAG_RETRIEVE_STUB_SCHEMA,
]

TOOL_FUNCTIONS: dict[str, ToolFunction] = {
    "calculator": calculator,
    "file_reader": file_reader,
    "web_search": web_search,
    "rag_retrieve_stub": rag_retrieve_stub,
}


def get_tool_schemas() -> list[dict[str, Any]]:
    return TOOL_SCHEMAS


def _build_tool_message(
        tool_call: dict[str, Any],
        result: ToolExecutionResult,
) -> dict[str, Any]:
    return {
        "role": "tool",
        "tool_call_id": tool_call.get("id"),
        "content": result.model_dump_json(),
    }


async def execute_tool_call(
        tool_call: dict[str, Any],
) -> tuple[dict[str, Any], ToolCallRecord, list[Source]]:
    function_data = tool_call.get("function", {})
    tool_name = function_data.get("name")
    raw_arguments = function_data.get("arguments") or "{}"

    if not tool_name:
        result = ToolExecutionResult(
            content={
                "error": "Tool call does not contain function name.",
            }
        )

        return (
            _build_tool_message(tool_call, result),
            ToolCallRecord(name="unknown", input={}),
            [],
        )
    
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        arguments = {}

    tool_record = ToolCallRecord(
        name=tool_name,
        input=arguments,
    )

    tool_func = TOOL_FUNCTIONS.get(tool_name)

    if tool_func is None:
        result = ToolExecutionResult(
            content={
                "tool": tool_name,
                "error": "Unknown tool",
            }
        )

        return _build_tool_message(tool_call, result), tool_record, []
    
    try:
        result = await tool_func(**arguments)
    except Exception as exc:
        result = ToolExecutionResult(
            content={
                "tool": tool_name,
                "arguments": arguments,
                "error": str(exc),
            }
        )

    return _build_tool_message(tool_call, result), tool_record, result.sources
