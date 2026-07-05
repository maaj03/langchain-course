from __future__ import annotations

import argparse
import os

from .models import ChatRequest, UserMetadata
from .service import ITAssistant


async def run() -> None:
    parser = argparse.ArgumentParser(description="Agente N1 de suporte de TI")
    parser.add_argument(
        "--session-id", default=os.getenv("DEV_SESSION_ID", "local-dev")
    )
    parser.add_argument("--name", default=os.getenv("DEV_USER_NAME"))
    parser.add_argument("--email", default=os.getenv("DEV_USER_EMAIL"))
    parser.add_argument("--json", dest="json_payload")
    args = parser.parse_args()
    assistant = ITAssistant()

    if args.json_payload:
        request = ChatRequest.model_validate_json(args.json_payload)
        response = await assistant.ainvoke(request)
        print(response.model_dump_json(indent=2))
        return

    metadata = UserMetadata(
        Session_ID=args.session_id,
        name=args.name,
        email=args.email,
    )
    print("IT Assistant iniciado. Digite 'sair' para encerrar.")
    while True:
        text = input("Você: ").strip()
        if text.lower() in {"sair", "exit", "quit"}:
            break
        response = await assistant.ainvoke(
            ChatRequest(
                sessionId=args.session_id,
                chatInput=text,
                metadata=metadata,
            )
        )
        print(f"Agente: {response.message}")
