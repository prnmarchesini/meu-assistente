# Runbook de Deploy (Passo 7)

Arquitetura em produção: **backend FastAPI** (API + IA + webhook do Telegram num
único serviço) e **frontend** (estático) — ambos no Railway, ligados ao repositório
`prnmarchesini/meu-assistente`.

## 1. Banco (Supabase) — já feito
- Schema aplicado (`schema_controle_gastos.sql`): 11 tabelas + `telegram_conversas`,
  pgvector, RLS.
- Buckets `pdfs` e `imagens` criados e **privados**.

## 2. Serviço Backend (Railway)
- **Root Directory:** `Back`
- Builder: NIXPACKS (já configurado em `Back/railway.json`); start:
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; healthcheck `/health`.
- **Variables** (aba Variables do serviço):
  - `SUPABASE_URL` = https://gewglofvtslhpcbswoeu.supabase.co
  - `SUPABASE_ANON_KEY` = (painel Supabase > Settings > API)
  - `SUPABASE_SERVICE_KEY` = (painel Supabase > Settings > API) — necessária p/ upload ao Storage
  - `SUPABASE_POOLER_URL` = a connection string do **session pooler (5432)**
  - `SUPABASE_TRANSACTION_URL` = a do transaction pooler (6543) — opcional
  - `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`
  - `TELEGRAM_BOT_TOKEN` = token do BotFather
  - `TELEGRAM_WEBHOOK_SECRET` = uma string aleatória forte (você define)
  - `TELEGRAM_BOT_USERNAME` = usuário do bot (sem @), p/ o deep link — opcional
  - `CORS_ORIGINS` = URL pública do frontend (ex.: https://front.up.railway.app)
  - `AMBIENTE` = producao

## 3. Serviço Frontend (Railway)
- **Root Directory:** `Front`
- Build: `npm run build`; start: `npm run start` (serve estático em `$PORT`).
- **Variables (build-time — Vite injeta no bundle):**
  - `VITE_SUPABASE_URL` = https://gewglofvtslhpcbswoeu.supabase.co
  - `VITE_SUPABASE_ANON_KEY` = a anon key
  - `VITE_API_URL` = URL pública do backend (ex.: https://back.up.railway.app)
- Após mudar variáveis VITE_, **rebuild** (elas entram no bundle no build).

## 4. Webhook do Telegram
Depois do backend no ar, registre o webhook (com o secret):
```
cd Back
python scripts/set_webhook.py https://SEU-BACKEND.up.railway.app
```
O webhook só aceita chamadas com o header `X-Telegram-Bot-Api-Secret-Token` igual a
`TELEGRAM_WEBHOOK_SECRET` (validado em toda chamada) + rate limit por IP.

## 5. Checklist de hardening (já no código)
- [x] Webhook valida o secret em toda chamada (403 sem ele).
- [x] Rate limit no webhook (60/min por IP).
- [x] Logs estruturados (JSON) com redação de campos sensíveis.
- [x] Timeout + retry nas APIs externas (OpenAI/DeepSeek); mensagem amigável.
- [x] Buckets privados.
- [x] CORS restrito por `CORS_ORIGINS` em produção.
- [x] Frontend usa só URL + anon key; service key só no backend.

## 6. Smoke test em produção
1. `GET https://BACK/health` → `{"status":"ok","supabase":true}`.
2. Abrir o frontend, cadastrar/login, lançar uma despesa parcelada.
3. Enviar nota (upload) e conferir extração.
4. No perfil, gerar código e vincular o Telegram; mandar "gastei 50 no mercado".
```
