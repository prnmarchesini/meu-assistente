# PASSO 6 — Telegram

**Pré-requisito:** Passo 5 verde (`/chat` funcionando pelo site).

**Objetivo:** tudo que o site faz, o Telegram faz por conversa — reusando o motor do
Passo 5. O bot é um adaptador fino, sem regra de negócio.

## `telegram/` 
1. Webhook que recebe updates e identifica o usuário pelo `telegram_chat_id`.
2. Vínculo por código:
   - Tela de perfil no React gera código (6 dígitos, expira em 5–10 min, uso único)
     + deep link `t.me/<bot>?start=CODIGO`.
   - O webhook consome `/start CODIGO` + o chat_id real → acha o user_id pelo código
     → grava `telegram_chat_id` no `profiles` → marca o código como usado.
   - `telegram_chat_id` é único (um chat = uma conta).
   - Botão "Desvincular" no perfil limpa o chat_id (decisão 20).
3. Roteamento das mensagens (tudo delega ao motor):
   - Texto → `orquestrador` (Passo 5).
   - Áudio → Whisper (transcreve/traduz p/ PT, decisão 14) → mostra a transcrição
     (decisão 13) → `orquestrador`.
   - Foto de nota → pipeline do Passo 4 → tela/sugestão de despesa.
4. Confirmação antes de gravar (decisão 12): o bot resume e espera "sim".
5. Chat não vinculado → instrui a habilitar pelo site.

## Critério de aceite
- Vincular a conta pelo deep link funciona e é uso único; vínculo expira.
- Lançar gasto por texto e por áudio funciona, com confirmação.
- Enviar foto de nota fiscal gera documento + sugestão de despesa.
- Desvincular pelo perfil corta o acesso daquele chat.

**Nenhuma lógica de negócio dentro de `telegram/` — só transporte e confirmação.**
