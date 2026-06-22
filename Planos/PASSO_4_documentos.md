# PASSO 4 — Documentos (notas fiscais e garantias)

**Pré-requisito:** Passo 3 verde (app usável e seguro pelo site).

**Objetivo:** subir uma nota (PDF ou imagem) e ela virar dados estruturados + busca.

## Pipeline (`ia/pipeline_doc.py` + serviços de documento)
1. Upload aos buckets: PDF → `pdfs`, imagem → `imagens` (privados, via service key).
   Gravar `bucket` + `path` em `documentos`.
2. Roteamento pelo bucket:
   - `pdfs` → extrair texto nativo com `pymupdf`; cair para OCR (GPT-4o vision)
     somente se o PDF não tiver texto (escaneado).
   - `imagens` → direto ao GPT-4o vision.
3. Estruturação com GPT-4o: extrair `fornecedor`, `valor_total`, `data_documento`,
   `fim_garantia`, `tipo_documento` → gravar em **colunas reais**.
4. Embedding do texto (`text-embedding-3-small`, 1536) em `documentos.embedding`.
5. A partir de uma nota fiscal, propor uma despesa pré-preenchida — **não salvar
   sozinho** (decisão 5): tela de revisão editável confirma (decisão 6).

## Consultas
- `garantias_a_vencer(user_id, dias)` → SQL puro sobre `fim_garantia`.
- `buscar_documento(user_id, consulta)` → similaridade pgvector + filtros
  estruturados (fornecedor, período, tipo) (decisão 16).

## Frontend
- Tela de upload (aceita PDF e imagem; manda pro bucket certo).
- Tela de revisão da nota (campos extraídos, editáveis) → confirma e cria despesa.
- Lista de documentos e de garantias ordenadas por vencimento (decisão 17).

## Critério de aceite
- Upload de um PDF e de uma imagem geram `documentos` com campos estruturados e
  embedding salvos.
- `garantias_a_vencer(30)` retorna corretamente por data.
- Busca semântica encontra um documento por descrição vaga do conteúdo.
- Uma nota fiscal gera uma sugestão de despesa que só persiste após confirmação.
