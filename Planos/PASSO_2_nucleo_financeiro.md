# PASSO 2 — Núcleo financeiro (PORTÃO CRÍTICO)

**Pré-requisito:** Passo 1 verde (`/health` conecta).

**Objetivo:** as regras de negócio puras, testadas, sem HTTP. É a fase que sustenta
todo o resto — não avance com teste vermelho.

## O que construir (em `backend/app/servicos/`)
Funções Python puras que recebem a conexão/sessão como dependência e **sempre**
filtram por `user_id`.

1. CRUD de `categorias`, `subcategorias`, `locais`, `contas`, `cartoes`.
   - Normalizar nomes: `trim` + comparação case-insensitive (decisão 18).
2. `faturas.py` → `obter_ou_criar_fatura(user_id, cartao, competencia)`.
   - Fatura sob demanda; respeitar `unique (cartao_id, competencia)`;
     `competencia` sempre no dia 01.
3. `parcelas.py` → `alocar_parcelas(user_id, cartao, data_compra, n_parcelas, valor)`:
   - acha a fatura da 1ª parcela comparando `data_compra` com `dia_fechamento`;
   - distribui as demais nas faturas consecutivas;
   - ajusta o resto da divisão para que `sum(parcelas) == valor` exatamente.
4. `despesas.py` → `criar_despesa(...)`:
   - valida coerência conta×cartão (espelha o CHECK do banco);
   - se cartão, dispara `alocar_parcelas`; se conta, sem parcelas.
   - edição/exclusão conforme decisões 7 e 8 (re-alocar; bloquear parcela em
     fatura paga).

## Testes obrigatórios (pytest) — casos de borda
- Compra ANTES do dia de fechamento → cai na fatura do mês corrente.
- Compra DEPOIS do fechamento → cai na fatura seguinte.
- Virada de ano: compra em dezembro que cai na fatura de janeiro.
- 100,00 em 3x → 33,34 + 33,33 + 33,33 (soma exata).
- À vista no cartão → 1 parcela.
- Despesa por conta → nenhuma parcela.
- Normalização: "Mercado" e "mercado" não criam duas categorias.

## Critério de aceite
- Suite de testes 100% verde, com os casos acima explícitos.
- Para qualquer despesa, `sum(parcelas.valor) == despesa.valor_total`.

**NÃO construa API nem UI aqui. Rode os testes, mostre o resultado e pare.**
