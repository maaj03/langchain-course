from __future__ import annotations

import json
from typing import Any

import httpx
from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from .config import Settings
from .models import CatalogToolInput, OpenTicketToolInput, UserMetadata


async def _call_n8n(
    url: str,
    payload: dict[str, Any],
    settings: Settings,
) -> str:
    """Encaminha a chamada; toda a lógica da tool permanece no workflow n8n."""
    async with httpx.AsyncClient(
        auth=settings.basic_auth,
        timeout=settings.request_timeout_seconds,
        follow_redirects=False,
    ) as client:
        response = await client.post(url, json=payload)
    response.raise_for_status()
    try:
        return json.dumps(response.json(), ensure_ascii=False)
    except ValueError:
        return response.text


def webhook_tools(settings: Settings, metadata: UserMetadata) -> list[BaseTool]:
    tools: list[BaseTool] = []

    if settings.n8n_catalog_webhook_url:

        async def call_catalog(query: str, known_fields: dict[str, Any]) -> str:
            return await _call_n8n(
                settings.n8n_catalog_webhook_url,
                {"query": query, "known_fields": known_fields},
                settings,
            )

        tools.append(
            StructuredTool.from_function(
                coroutine=call_catalog,
                name="SW_FS_TICKETS_RETRIEVER1",
                description=(
                    "Chama a tool de catálogo existente no n8n para obter classificação, "
                    "campos obrigatórios, tipos e opções válidas."
                ),
                args_schema=CatalogToolInput,
            )
        )

    async def call_open_ticket(
        subject: str,
        description: str,
        request_type: str,
        category: str | None = None,
        subcategory: str | None = None,
        item: str | None = None,
        urgency: str | None = None,
        impact: str | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> str:
        ticket = OpenTicketToolInput.model_validate(
            {
                "subject": subject,
                "description": description,
                "request_type": request_type,
                "category": category,
                "subcategory": subcategory,
                "item": item,
                "urgency": urgency,
                "impact": impact,
                "additional_fields": additional_fields or {},
            }
        )
        name = metadata.requester_name
        email = metadata.requester_address
        if not name or not email:
            return json.dumps(
                {
                    "error": "requester_not_authenticated",
                    "message": "É necessário estar logado no CSC para receber atendimento.",
                },
                ensure_ascii=False,
            )

        payload = ticket.model_dump(exclude_none=True)
        payload.update(
            {
                "name": name,
                "email": email,
                "sessionId": metadata.session_id,
                "conversation_id": metadata.conversation_id,
            }
        )
        return await _call_n8n(
            settings.n8n_open_ticket_webhook_url,
            payload,
            settings,
        )

    tools.append(
        StructuredTool.from_function(
            coroutine=call_open_ticket,
            name="OPEN_TCKT_FRESH",
            description="Chama a tool de abertura de chamado que já existe no n8n.",
            args_schema=OpenTicketToolInput,
        )
    )
    return tools


async def mcp_tools(settings: Settings) -> list[BaseTool]:
    """Descobre e usa as tools do RAG diretamente no MCP publicado pelo n8n."""
    client = MultiServerMCPClient(
        {
            "n8n_rag": {
                "transport": "http",
                "url": settings.n8n_mcp_url,
            }
        },
        tool_name_prefix=True,
    )
    return await client.get_tools()
