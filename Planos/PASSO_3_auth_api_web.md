# PASSO 3 — Auth + API + Web básico

**Pré-requisito:** Passo 2 verde (testes de serviço passando).

**Objetivo:** usar o app pelo site, multiusuário e seguro.

## Backend (`api/`)
1. Rotas REST expondo os serviços do Passo 2.
2. Middleware que valida o JWT do Supabase e extrai o `user_id`, injetando-o nas
   funções de serviço. **O frontend nunca envia user_id.**
3. Endpoints de leitura para o dashboard (decisão 19): total do mês, próxima
   fatura, garantias a vencer, últimas despesas.

## Frontend (React)
1. Supabase Auth: signup (com confirmação de e-mail), login, logout, sessão
   persistente, "esqueci a senha" (decisão 20).
2. Telas: cadastro de usuário, login, e o **dashboard** como tela inicial.
3. CRUD de categorias/subcategorias, contas e cartões.
4. Tela de lançar despesa: data padrão hoje (decisão 2), forma de pagamento, e nº
   de parcelas quando for cartão (decisão 3). Categoria/local opcionais.
5. Seed opcional de categorias no primeiro login (decisão 4).
6. Tela de fatura: parcelas do mês + comprometimento futuro; botão "marcar paga"
   (decisão 9).

## Segurança
- O React usa apenas `SUPABASE_URL` + `SUPABASE_ANON_KEY`.
- RLS já está habilitada (Passo 1). Confirme que as queries do front respeitam o
  JWT do usuário logado.

## Critério de aceite
- Login/logout funcionam; a sessão sobrevive a refresh.
- Lançar uma despesa parcelada pela UI cria as parcelas nas faturas certas.
- **Teste de RLS:** logue com dois usuários diferentes e confirme que um não
  enxerga nenhum dado do outro. (Forneça um roteiro para eu executar esse teste.)

**Pare após o teste de RLS com dois usuários passar.**
