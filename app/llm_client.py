from typing import Any

from collections.abc import AsyncIterator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.config import settings
from app.prompts import SYSTEM_PROMPT


class LLMClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )

    def _build_extra_body(self) -> dict:
        return {
            "reasoning": {
                "effort": "none",
                "enabled": False,
            },
        }
    
    def _ensure_configured(self) -> None:
        if not settings.llm_api_key:
            raise RuntimeError(
                "LLM_API_KEY is not set. Create a '.env' file based on '.env.example'"
            )
        
    async def create_chat_completion(
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]] | None = None,
    ) -> ChatCompletion:
        self._ensure_configured()

        return await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            extra_body=self._build_extra_body(),
        )

    async def chat(self, user_message: str) -> str:
        completion = await self.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_message
                },
            ],
        )

        # with open("completion.json", "w", encoding="utf-8") as f:
        #     f.write(completion.model_dump_json(indent=2))

        return completion.choices[0].message.content or ""
    
    async def stream_chat(self, user_message: str) -> AsyncIterator[str]:
        self._ensure_configured()

        stream = await self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            stream=True,
            extra_body=self._build_extra_body(),
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta
