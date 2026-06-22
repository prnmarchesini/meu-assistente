# 00 — Decisões de usabilidade (travadas)

Estas decisões definem o comportamento do produto. Os arquivos de PASSO referenciam
este documento. Onde houver dúvida de implementação, esta é a fonte da verdade.

## Lançamento de despesas
**1. Categoria é obrigatória?**
Não no banco (pode ser nula). A UI permite "Sem categoria", mas sugere categorizar.
Relatórios agrupam "Sem categoria" à parte para o usuário perceber e corrigir.

**2. Qual a data padrão ao lançar uma despesa?**
Hoje, sempre editável. A data importa para o cálculo de fatura, então é um campo de
primeira classe, não escondido.

**3. Quais campos são obrigatórios no lançamento?**
Descrição, valor, data e forma de pagamento. Se for cartão, também o cartão e o
número de parcelas (padrão 1). Categoria, subcategoria e local são opcionais.

**4. O app começa vazio ou com dados de exemplo?**
No primeiro login, oferece um seed opcional de categorias comuns (Mercado,
Transporte, Saúde, Lazer, Moradia, Contas). O usuário pode pular. Contas e cartões
nunca são "seedados" — são pessoais.

**5. Subir uma nota fiscal cria a despesa automaticamente?**
Não. A IA pré-preenche e o usuário confirma numa tela de revisão. Isso evita que
extração errada suje o banco. A confirmação é um clique quando os dados vêm certos.

**6. E se a IA extrair os campos errados?**
A tela de revisão é 100% editável antes de salvar. O usuário corrige fornecedor,
valor, data e fim de garantia ali mesmo.

## Edição e exclusão
**7. Posso editar uma despesa parcelada?**
Sim. Mudar valor ou número de parcelas re-aloca as parcelas (apaga e recria). Uma
parcela que já está numa fatura marcada como paga fica bloqueada para edição —
avisa o usuário em vez de silenciosamente reescrever histórico.

**8. Posso excluir uma despesa parcelada?**
Sim, com cascade nas parcelas. Se alguma parcela estiver em fatura paga, pede
confirmação explícita antes.

**9. Como a fatura é marcada como paga?**
Manualmente, pelo usuário ("marcar fatura como paga"). Marcar paga não apaga nada —
só muda o status, preservando o histórico.

**10. Estorno / reembolso?**
Fora do MVP. Anotado como extensão futura (despesa de valor negativo).

**11. Moeda?**
Apenas BRL no MVP. Sem conversão.

## Telegram
**12. O bot confirma antes de salvar?**
Sim. Resume o que entendeu ("Mercado, R$200, 2x no Nubank — confirmar?") e só
executa após o "sim". Vale para despesas e qualquer escrita.

**13. A transcrição de áudio é mostrada?**
Sim. O bot devolve em texto o que entendeu e segue o mesmo fluxo de confirmação,
para o usuário pegar erro de transcrição antes de virar dado.

**14. E se o áudio vier em outro idioma?**
O Whisper transcreve/traduz para PT-BR e o app opera em PT. É o uso de "tradução por
áudio" que estava no escopo.

## Documentos e garantias
**15. Nota com vários itens vira quantas despesas?**
Uma despesa com o valor total no MVP; os itens ficam preservados em `texto_extraido`
e no embedding (busca encontra). Quebrar por item é extensão futura.

**16. Como busco um documento antigo?**
Busca semântica (pgvector) por descrição vaga do conteúdo + filtros estruturados
(fornecedor, período, tipo de documento).

**17. O app avisa antes de uma garantia ou fatura vencer?**
No MVP, telas listam garantias e faturas ordenadas por vencimento. Alerta proativo
pelo Telegram é a Fase 7 (job agendado).

## Geral
**18. Nomes duplicados (ex: "Mercado" vs "mercado")?**
Normalizar antes de inserir: `trim` + comparação case-insensitive, além do `unique`
do banco. Evita categorias quase-iguais poluindo os relatórios.

**19. O que o usuário vê ao logar?**
Um dashboard: total gasto no mês, próxima fatura a vencer, garantias vencendo em 30
dias e as últimas despesas. É a tela inicial.

**20. Cadastro, senha e desvincular Telegram?**
Signup com confirmação de e-mail (config do Supabase Auth). "Esqueci a senha" usa o
reset do Supabase. No perfil há um botão "Desvincular Telegram" que limpa o
`telegram_chat_id` e põe `telegram_habilitado = false`.
