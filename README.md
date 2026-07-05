# IT Assistant

Agente LangChain/LangGraph que substitui somente o **AI Agent** do n8n. O RAG, a
consulta de catálogo e a abertura no Freshservice continuam hospedados no n8n e são
chamados remotamente pelo MCP e pelos webhooks existentes.

## Configuração

Copie `.env.example` para `.env` e preencha Azure OpenAI, MCP e webhooks. URLs reais
de webhook/MCP não devem ser commitados.

```powershell
Copy-Item .env.example .env
uv sync
uv run python main.py --name "Seu Nome" --email "voce@empresa.com"
```

O payload do Chat Trigger também pode ser enviado com `--json`. A memória é isolada
pelo `sessionId`; `DATABASE_URL` habilita persistência PostgreSQL em produção.

## Fronteira da solução

- `it_assistant/n8n_tools.py` apenas encaminha chamadas HTTP e carrega tools do MCP.
- Toda consulta ao RAG/Supabase permanece no workflow MCP do n8n.
- Toda abertura de chamado permanece no workflow `OPEN_TCKT_FRESH` do n8n.
- Nome e e-mail são injetados do contexto autenticado e nunca solicitados ao usuário.
