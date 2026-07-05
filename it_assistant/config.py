from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Configure {name} no arquivo .env.")
    return value


def _optional(name: str) -> str | None:
    return os.getenv(name, "").strip() or None


@dataclass(frozen=True, slots=True)
class Settings:
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str
    azure_openai_api_version: str
    n8n_catalog_webhook_url: str | None
    n8n_open_ticket_webhook_url: str
    n8n_mcp_url: str
    n8n_username: str | None
    n8n_password: str | None
    database_url: str | None
    request_timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            azure_openai_api_key=_required("AZURE_OPENAI_API_KEY"),
            azure_openai_endpoint=_required("AZURE_OPENAI_ENDPOINT"),
            azure_openai_deployment=os.getenv(
                "AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini"
            ),
            azure_openai_api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION", "2025-04-01-preview"
            ),
            n8n_catalog_webhook_url=_optional("N8N_CATALOG_WEBHOOK_URL"),
            n8n_open_ticket_webhook_url=_required("N8N_OPEN_TICKET_WEBHOOK_URL"),
            n8n_mcp_url=_required("N8N_MCP_URL"),
            n8n_username=_optional("N8N_BASIC_AUTH_USERNAME"),
            n8n_password=_optional("N8N_BASIC_AUTH_PASSWORD"),
            database_url=_optional("DATABASE_URL"),
            request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        )

    @property
    def basic_auth(self) -> tuple[str, str] | None:
        if self.n8n_username and self.n8n_password:
            return self.n8n_username, self.n8n_password
        return None
