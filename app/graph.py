from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.config import settings
from app.llm_client import LLMClient
from app.prompts import SYSTEM_PROMPT
from app.schemas import ChatResponse, Source, ToolCallRecord
from app.tools.registry import execute_tool_call, get_tool_schemas


class AgentState(TypedDict, total=False):
    messages: list[dict[str, Any]]
    response: ChatResponse
    used_tools: list[ToolCallRecord]
    sources: list[Source]
    steps: int


def build_initial_messages(user_message: str) -> list[dict[str, Any]]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]


def build_agent_graph(llm_client: LLMClient):
    graph = StateGraph(AgentState)

    async def call_model(state: AgentState) -> AgentState:
        messages = state["messages"]
        steps = state.get("steps", 0)

        completion = await llm_client.create_chat_completion(
            messages=messages,
            tools=get_tool_schemas(),
        )

        assistant_message = completion.choices[0].message.model_dump(exclude_none=True)

        return {
            "messages": [*messages, assistant_message],
            "steps": steps + 1,
        }

    async def execute_tools(state: AgentState) -> AgentState:
        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = last_message.get("tool_calls") or []

        tool_messages: list[dict[str, Any]] = []
        used_tools = list(state.get("used_tools", []))
        sources = list(state.get("sources", []))

        for tool_call in tool_calls:
            tool_message, tool_record, tool_sources = await execute_tool_call(tool_call)

            tool_messages.append(tool_message)
            used_tools.append(tool_record)
            sources.extend(tool_sources)

        return {
            "messages": [*messages, *tool_messages],
            "used_tools": used_tools,
            "sources": sources,
        }

    async def build_response(state: AgentState) -> AgentState:
        messages = state["messages"]

        answer = ""

        for message in reversed(messages):
            if message.get("role") == "assistant" and message.get("content"):
                answer = message["content"]
                break

        if not answer:
            answer = "Не удалось получить финальный текстовый ответ от модели."

        response = ChatResponse(
            answer=answer,
            used_tools=state.get("used_tools", []),
            sources=state.get("sources", []),
            confidence="medium",
        )

        return {
            "response": response,
        }

    def route_after_model(state: AgentState) -> Literal["tools", "final"]:
        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = last_message.get("tool_calls")
        steps = state.get("steps", 0)

        if tool_calls and steps < settings.max_agent_steps:
            return "tools"

        return "final"

    graph.add_node("call_model", call_model)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("build_response", build_response)

    graph.add_edge(START, "call_model")

    graph.add_conditional_edges(
        "call_model",
        route_after_model,
        {
            "tools": "execute_tools",
            "final": "build_response",
        },
    )

    graph.add_edge("execute_tools", "call_model")
    graph.add_edge("build_response", END)

    return graph.compile()
