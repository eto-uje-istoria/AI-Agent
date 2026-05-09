import asyncio
from typing import Any

from tavily import TavilyClient # type: ignore[import-untyped]

from app.config import settings
from app.schemas import Source
from app.tools.base import ToolExecutionResult


async def web_search(query: str, max_results: int = 5) -> ToolExecutionResult:
    if not settings.tavily_api_key:
        return ToolExecutionResult(
            content={
                "query": query,
                "error": "TAVILY_API_KEY is not set.",
            }
        )
    
    client = TavilyClient(api_key=settings.tavily_api_key)

    try:
        result = await asyncio.to_thread(
            client.search,
            query=query,
            max_results=max_results,
        )

        raw_results = result.get("results", [])

        simplified_results = [
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "score": item.get("score"),
            }
            for item in raw_results
        ]

        sources = [
            Source(
                title=item.get("title"),
                url=item.get("url"),
            )
            for item in raw_results
            if item.get("url")
        ]

        return ToolExecutionResult(
            content={
                "query": query,
                "results": simplified_results,
            },
            sources=sources
        )

    except Exception as exc:
        return ToolExecutionResult(
            content={
                "query": query,
                "error": str(exc),
            }
        )
    

WEB_SEARCH_SCHEMA: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current or external information using Tavily.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results.",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },   
}
