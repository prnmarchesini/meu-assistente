# meu-assistente — Controle de Gastos

Assistente financeiro pessoal: registre e consulte gastos pela web, por conversa
(linguagem natural) e pelo Telegram (texto, áudio e foto de nota fiscal). Extrai
dados de documentos com IA e faz busca semântica.

## Arquitetura
- **Backend** (`Back/`): FastAPI (Python). Regras de negócio puras e testadas,
  API REST, motor de IA (DeepSeek orquestrando function calling) e webhook do
  Telegram num único serviço.
- **Frontend** (`Front/`): React + Vite + Supabase Auth.
- **Banco**: Supabase (Postgres + pgvector + Auth + Storage). RLS por usuário.
- **IA**: OpenAI (GPT-4o visão/estruturação, Whisper, embeddings) + DeepSeek (chat
  com ferramentas). Nenhum cálculo financeiro é feito pelo LLM — vem dos serviços.

## Estrutura
```
Back/
  app/
    core/        config, db, supabase, logging, ratelimit
    servicos/    cadastros, faturas, parcelas, despesas, documentos, relatorios,
                 dashboard, telegram_vinculo  (regras de negócio, filtram por user_id)
    ia/          openai_client, pipeline_doc, tools, orquestrador
    api/         auth (JWT/JWKS), deps, schemas, rotas, rotas_documentos,
                 rotas_chat, rotas_telegram
    telegram/    bot, webhook
    main.py      FastAPI (/health + routers)
  tests/         121 testes (puros + integração em transação revertida)
Front/           React (auth, dashboard, despesas, faturas, upload, chat, perfil)
schema_controle_gastos.sql   schema do banco (rode no Supabase)
docs/            ROTEIRO_RLS.md, DEPLOY.md
```

## Rodar localmente
Backend:
```
cd Back
pip install -r requirements.txt
cp .env.example .env   # preencha as chaves
uvicorn app.main:app --reload
```
Frontend:
```
cd Front
npm install
cp .env.example .env   # VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL
npm run dev
```
Testes do backend: `cd Back && pytest`

## Deploy
Veja `docs/DEPLOY.md` (Railway: backend + frontend, variáveis, setWebhook).

## Construído nos 7 passos
Fundação → núcleo financeiro (testado) → auth/API/web → documentos → motor de IA →
Telegram → produção. Cada passo com seu portão de verificação. Planos em `Planos/`.
