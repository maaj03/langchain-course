import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ["LANGSMITH_TRACING"] = "false"

from it_assistant.config import Settings
from it_assistant.models import UserMetadata
from it_assistant.n8n_tools import webhook_tools


def test_settings() -> Settings:
    return Settings(
        azure_openai_api_key="test",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_deployment="deployment",
        azure_openai_api_version="2025-04-01-preview",
        n8n_catalog_webhook_url="https://n8n.example/catalog",
        n8n_open_ticket_webhook_url="https://n8n.example/open",
        n8n_mcp_url="https://n8n.example/mcp/test",
        n8n_username="user",
        n8n_password="pass",
        database_url=None,
        request_timeout_seconds=10,
    )


class N8nToolTests(unittest.TestCase):
    def test_open_ticket_only_forwards_and_injects_identity(self) -> None:
        metadata = UserMetadata(
            Session_ID="sess-1",
            conversation_id="conv-1",
            name="Maria",
            email="maria@example.com",
        )
        tool = next(
            tool
            for tool in webhook_tools(test_settings(), metadata)
            if tool.name == "OPEN_TCKT_FRESH"
        )

        with patch(
            "it_assistant.n8n_tools._call_n8n",
            new=AsyncMock(return_value='{"message":"ok"}'),
        ) as call:
            result = asyncio.run(
                tool.ainvoke(
                    {
                        "subject": "VPN",
                        "description": "VPN não conecta",
                        "request_type": "Incidente",
                    }
                )
            )

        self.assertEqual(result, '{"message":"ok"}')
        payload = call.await_args.args[1]
        self.assertEqual(payload["name"], "Maria")
        self.assertEqual(payload["email"], "maria@example.com")
        self.assertEqual(payload["sessionId"], "sess-1")

    def test_open_ticket_does_not_call_n8n_without_identity(self) -> None:
        tool = next(
            tool
            for tool in webhook_tools(test_settings(), UserMetadata())
            if tool.name == "OPEN_TCKT_FRESH"
        )
        with patch("it_assistant.n8n_tools._call_n8n", new=AsyncMock()) as call:
            result = asyncio.run(
                tool.ainvoke(
                    {
                        "subject": "VPN",
                        "description": "VPN não conecta",
                        "request_type": "Incidente",
                    }
                )
            )
        call.assert_not_awaited()
        self.assertIn("requester_not_authenticated", result)


if __name__ == "__main__":
    unittest.main()
