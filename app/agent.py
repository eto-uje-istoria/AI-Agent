from collections.abc import AsyncIterator

from app.graph import AgentState, build_agent_graph, build_initial_messages
from app.llm_client import LLMClient
from app.schemas import ChatRequest, ChatResponse
from app.utils.sse import sse_event


class AgentService:
    def __init__(self) -> None:
        self.llm_client = LLMClient()
        self.graph = build_agent_graph(self.llm_client)

    async def run(self, request: ChatRequest) -> ChatResponse:
        result: AgentState = await self.graph.ainvoke(
            {
                "messages": build_initial_messages(request.message),
                "used_tools": [],
                "sources": [],
                "steps": 0,
            }
        )

        return result["response"]

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        yield sse_event(
            "start",
            {
                "message": "started",
            },
        )

        chunks: list[str] = []

        async for delta in self.llm_client.stream_chat(request.message):
            chunks.append(delta)

            yield sse_event(
                "delta",
                {
                    "text": delta,
                },
            )

        answer = "".join(chunks).strip()

        response = ChatResponse(
            answer=answer,
            used_tools=[],
            sources=[],
            confidence="medium",
        )

        yield sse_event(
            "final",
            response.model_dump(),
        )
        