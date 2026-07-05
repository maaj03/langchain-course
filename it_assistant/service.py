from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from .config import Settings
from .models import ChatRequest, ChatResponse
from .n8n_tools import mcp_tools, webhook_tools
from .prompt import SYSTEM_PROMPT


class ITAssistant:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self._memory = InMemorySaver()

    def _model(self) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            azure_deployment=self.settings.azure_openai_deployment,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
            temperature=0,
        )

    @asynccontextmanager
    async def _checkpointer(self) -> AsyncIterator[Any]:
        if not self.settings.database_url:
            yield self._memory
            return
        async with AsyncPostgresSaver.from_conn_string(
            self.settings.database_url
        ) as checkpointer:
            await checkpointer.setup()
            yield checkpointer

    async def ainvoke(self, request: ChatRequest) -> ChatResponse:
        metadata = request.metadata
        if not metadata.session_id:
            metadata = metadata.model_copy(update={"session_id": request.session_id})
        tools = webhook_tools(self.settings, metadata)
        tools.extend(await mcp_tools(self.settings))
        prompt = SYSTEM_PROMPT.format(
            requester_name=metadata.requester_name or "não disponível",
            requester_email=metadata.requester_address or "não disponível",
        )

        async with self._checkpointer() as checkpointer:
            agent = create_agent(
                model=self._model(),
                tools=tools,
                system_prompt=prompt,
                checkpointer=checkpointer,
                name="it_assistant",
            )
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": request.chat_input}]},
                {"configurable": {"thread_id": request.session_id}},
            )

        content = result["messages"][-1].content
        return ChatResponse(
            session_id=request.session_id,
            message=content if isinstance(content, str) else str(content),
        )
