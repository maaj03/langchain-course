from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class UserMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    conversation_id: str | None = None
    session_id: str | None = Field(default=None, alias="Session_ID")
    name: str | None = None
    email: str | None = None
    full_name: str | None = None
    requester_email: str | None = None

    @property
    def requester_name(self) -> str | None:
        return self.name or self.full_name

    @property
    def requester_address(self) -> str | None:
        return self.email or self.requester_email


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: str = "sendMessage"
    session_id: str = Field(alias="sessionId")
    chat_input: str = Field(alias="chatInput", min_length=1)
    metadata: UserMetadata = Field(default_factory=UserMetadata)


class CatalogToolInput(BaseModel):
    query: str = Field(description="Problema ou necessidade em linguagem natural.")
    known_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Respostas já coletadas para o workflow continuar a classificação.",
    )


class OpenTicketToolInput(BaseModel):
    subject: str = Field(description="Resumo curto do chamado.")
    description: str = Field(description="Descrição completa do chamado.")
    request_type: Literal["Incidente", "Requisição"]
    category: str | None = None
    subcategory: str | None = None
    item: str | None = None
    urgency: str | None = None
    impact: str | None = None
    additional_fields: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    session_id: str
    message: str
