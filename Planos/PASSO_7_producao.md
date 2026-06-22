# PASSO 7 — Produção (deploy + hardening)

**Pré-requisito:** Passo 6 verde (fluxo completo funcionando local).

**Objetivo:** rodando no ar, seguro.

## Deploy
1. Backend no Railway: variáveis cadastradas no painel (o `.env` não sobe).
   Backend + IA + webhook do Telegram rodam no mesmo serviço FastAPI.
2. `setWebhook` do Telegram apontando para a URL pública do backend, usando o
   `TELEGRAM_WEBHOOK_SECRET`.
3. Frontend em produção (Railway ou Vercel) com as envs públicas do Supabase
   (`SUPABASE_URL`, `SUPABASE_ANON_KEY`).

## Hardening
- Validar o secret token em **toda** chamada do webhook (rejeitar sem ele).
- Rate limit na rota do webhook.
- Logs estruturados (sem vazar segredos nem dados sensíveis das notas).
- Tratamento de falha das APIs externas (OpenAI/DeepSeek): timeout, retry e
  mensagem amigável ao usuário quando indisponível.
- Confirmar que os buckets `pdfs` e `imagens` continuam privados em produção.

## Critério de aceite
- Fluxo completo funciona em produção, pelo site e pelo Telegram.
- O webhook só aceita chamadas com o secret token correto.
- Nenhuma chave aparece em logs ou no bundle do frontend.

## Extensões futuras (pós-MVP, sem reabrir a base)
- Dashboard com gráficos (novas tools de leitura + telas).
- Alertas proativos no Telegram (job agendado: garantia/fatura a vencer).
- Exportação CSV das despesas e faturas.
- Estorno/reembolso e nota com múltiplos itens (decisões 10 e 15).
