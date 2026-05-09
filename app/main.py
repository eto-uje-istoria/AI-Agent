from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.agent import AgentService
from app.schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="AI Agent Core",
    version="0.1.0",
)

agent = AgentService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await agent.run(request)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        agent.stream(request),
        media_type="text/event-stream",
    )
