# PASSO 5 — Motor de IA (orquestrador DeepSeek)

**Pré-requisito:** Passo 4 verde (serviços + documentos prontos).

**Objetivo:** conversa em linguagem natural manipula o app inteiro, chamando as
funções já testadas. O LLM escolhe ferramentas; o Python calcula.

## `ia/tools.py` — catálogo de ferramentas
Uma tool por operação de serviço, cada uma um invólucro fino sobre `servicos/`.
**O `user_id` é injetado pelo orquestrador, nunca fornecido pelo modelo.**

Escrita:
- `criar_categoria(nome)`, `criar_subcategoria(categoria, nome)`
- `criar_local(nome)`, `criar_conta(nome, tipo)`
- `cadastrar_cartao(nome, dia_fechamento, dia_vencimento, bandeira?, limite?)`
- `criar_despesa(descricao, valor, data, categoria?, subcategoria?, local?,
  forma_pagamento, conta?|cartao?, num_parcelas)`
- `marcar_fatura_paga(cartao, competencia)`
- `vincular_documento_a_despesa(documento_id, despesa_id)`

Leitura / relatórios (tão importantes quanto a escrita):
- `consultar_fatura(cartao, competencia)`
- `proximas_faturas(cartao?)`
- `total_por_periodo(inicio, fim, agrupar_por?)`
- `total_por_categoria(periodo)`
- `garantias_a_vencer(dias=30)`
- `buscar_documento(consulta)`
- `listar_despesas(filtros)`

## `ia/orquestrador.py`
- Loop de function calling com o DeepSeek: recebe mensagem + user_id → modelo
  escolhe tools → executa a função real → devolve resultado ao modelo → repete até
  a resposta final.
- **Plano B:** se a versão do DeepSeek não suportar function calling, peça JSON
  estruturado e faça o dispatch manualmente.
- Confirmação de escrita: para ações que gravam, o orquestrador resume e pede
  confirmação antes de executar (decisão 12) — espelhando o comportamento do
  Telegram.

## Endpoint
- `POST /chat` para testar o motor pelo site **antes** do Telegram.

## Critério de aceite
- "Gastei 200 no mercado, parcelei em 2x no Nubank" → cria a despesa e as 2
  parcelas nas faturas certas, via chat.
- "Quanto gastei em mercado esse mês?" e "Quais garantias vencem em julho?" →
  respostas corretas (tools de leitura).
- Nenhum cálculo é feito pelo LLM — confirme que parcela/fatura saem dos serviços.
