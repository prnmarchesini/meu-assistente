# Roteiro — Teste de RLS com 2 usuários (portão do Passo 3)

Objetivo: confirmar que um usuário **não enxerga** dados de outro, mesmo a API e o
banco sendo compartilhados. A isolação vem de duas camadas: (1) os serviços sempre
filtram por `user_id` extraído do JWT; (2) o RLS do Postgres barra no banco.

## Pré-requisitos
- `SUPABASE_ANON_KEY` preenchido no `Back/.env` e `Front/.env`.
- Backend rodando: `cd Back && uvicorn app.main:app --reload`
- Frontend rodando: `cd Front && npm run dev`
- No painel do Supabase (Authentication > Providers > Email), confirmação de e-mail
  ligada ou desligada conforme preferir testar.

## Passos
1. **Usuário A**: cadastre `a@teste.com`, confirme o e-mail, faça login.
2. Crie um cartão "Cartão A" e lance uma despesa parcelada (ex.: R$ 200 em 2x).
   - Verifique em **Faturas** que as 2 parcelas caíram nas competências certas.
3. Saia (logout).
4. **Usuário B**: cadastre `b@teste.com`, confirme, faça login.
5. No Dashboard e em todas as telas, **B não deve ver** o cartão, a despesa nem as
   faturas de A. As listas começam vazias.
6. Crie dados próprios para B e confirme que A também não os vê (repita 3→1).

## Verificação extra (banco, opcional)
Com a anon key, uma query direta do supabase-js logado como B a `despesas` deve
retornar apenas as linhas de B — o RLS (`auth.uid() = user_id`) bloqueia o resto.

## Critério de aceite
- Login/logout funcionam e a sessão sobrevive a refresh (persistSession).
- Despesa parcelada criada pela UI gera parcelas nas faturas corretas.
- Nenhum dado de A aparece para B e vice-versa.
