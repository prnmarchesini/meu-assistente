# PASSO 1 — Fundação

**Pré-requisito:** nenhum. Leia `prompt_claude_code.md` (contexto-mestre da
arquitetura) e `00_decisoes_usabilidade.md` antes de começar.

**Objetivo:** o esqueleto do projeto sobe e fala com o Supabase. Sem regra de
negócio.

## O que construir
1. Estrutura de pastas:
   ```
   controle-gastos/
   ├── backend/app/{core,servicos,api,ia,telegram}/  + main.py
   ├── backend/{requirements.txt,.env,.env.example}
   ├── frontend/  (React)
   └── .gitignore   (1ª linha: .env)
   ```
2. `.env.example` com todas as chaves em branco: SUPABASE_URL, SUPABASE_ANON_KEY,
   SUPABASE_SERVICE_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, TELEGRAM_BOT_TOKEN,
   TELEGRAM_WEBHOOK_SECRET, SUPABASE_TRANSACTION_URL, SUPABASE_POOLER_URL,
   RAILWAY_TOKEN.
3. `core/config.py`: carrega o `.env` (pydantic-settings ou equivalente).
4. `core/supabase.py`: cliente Supabase usando a service key.
5. `main.py`: FastAPI com rota `GET /health` que testa a conexão ao Supabase.
6. React mínimo que renderiza uma tela "ok".

## Tarefas manuais do usuário (liste ao final)
- Rodar `schema_controle_gastos.sql` no SQL Editor do Supabase.
- Criar os buckets `pdfs` e `imagens` no Storage, ambos **privados**.
- Preencher o `.env` (você só usa o `.env.example` como modelo).

## Critério de aceite
- `GET /health` retorna ok e confirma a conexão com o Supabase.
- React abre no navegador.
- `git status` não mostra o `.env`.

**Pare ao terminar e confirme que o /health conecta antes do Passo 2.**
