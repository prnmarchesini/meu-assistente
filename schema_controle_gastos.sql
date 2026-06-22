-- schema_controle_gastos.sql
-- Schema do app de controle de gastos (Supabase / Postgres + pgvector).
-- Rode no SQL Editor do Supabase. Idempotente o suficiente para reexecucao em DEV.
-- RLS habilitada em todas as tabelas; o backend usa a SERVICE KEY (bypassa RLS)
-- e SEMPRE filtra por user_id no codigo. O frontend usa a ANON KEY + JWT e
-- depende das policies abaixo.

-- ───────────────────────────── Extensoes ─────────────────────────────
create extension if not exists vector;

-- ───────────────────────────── profiles ─────────────────────────────
-- 1:1 com auth.users. Guarda o vinculo do Telegram.
create table if not exists public.profiles (
  id                   uuid primary key references auth.users(id) on delete cascade,
  email                text,
  telegram_chat_id     bigint unique,
  telegram_habilitado  boolean not null default false,
  criado_em            timestamptz not null default now()
);

-- Cria o profile automaticamente quando um usuario se cadastra no Auth.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ───────────────────────────── categorias ─────────────────────────────
create table if not exists public.categorias (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  nome       text not null,
  criado_em  timestamptz not null default now()
);
-- Unicidade case-insensitive por usuario (decisao 18).
create unique index if not exists categorias_user_nome_ux
  on public.categorias (user_id, lower(nome));

-- ─────────────────────────── subcategorias ───────────────────────────
create table if not exists public.subcategorias (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  categoria_id  uuid not null references public.categorias(id) on delete cascade,
  nome          text not null,
  criado_em     timestamptz not null default now()
);
create unique index if not exists subcategorias_user_cat_nome_ux
  on public.subcategorias (user_id, categoria_id, lower(nome));

-- ───────────────────────────── locais ─────────────────────────────
create table if not exists public.locais (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  nome       text not null,
  criado_em  timestamptz not null default now()
);
create unique index if not exists locais_user_nome_ux
  on public.locais (user_id, lower(nome));

-- ───────────────────────────── contas ─────────────────────────────
create table if not exists public.contas (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  nome       text not null,
  tipo       text,  -- corrente | poupanca | dinheiro | ...
  criado_em  timestamptz not null default now()
);
create unique index if not exists contas_user_nome_ux
  on public.contas (user_id, lower(nome));

-- ───────────────────────────── cartoes ─────────────────────────────
create table if not exists public.cartoes (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  nome           text not null,
  dia_fechamento int  not null check (dia_fechamento between 1 and 31),
  dia_vencimento int  not null check (dia_vencimento between 1 and 31),
  bandeira       text,
  limite         numeric(12,2),
  criado_em      timestamptz not null default now()
);
create unique index if not exists cartoes_user_nome_ux
  on public.cartoes (user_id, lower(nome));

-- ───────────────────────────── faturas ─────────────────────────────
-- Fatura sob demanda; competencia sempre no dia 01.
create table if not exists public.faturas (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  cartao_id    uuid not null references public.cartoes(id) on delete cascade,
  competencia  date not null,  -- sempre dia 01
  status       text not null default 'aberta' check (status in ('aberta','paga')),
  pago_em      timestamptz,
  criado_em    timestamptz not null default now(),
  unique (cartao_id, competencia)
);

-- ───────────────────────────── despesas ─────────────────────────────
create table if not exists public.despesas (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  descricao       text not null,
  valor_total     numeric(12,2) not null check (valor_total > 0),
  data            date not null,
  categoria_id    uuid references public.categorias(id)    on delete set null,
  subcategoria_id uuid references public.subcategorias(id) on delete set null,
  local_id        uuid references public.locais(id)        on delete set null,
  forma_pagamento text not null check (forma_pagamento in ('conta','cartao')),
  conta_id        uuid references public.contas(id)        on delete restrict,
  cartao_id       uuid references public.cartoes(id)       on delete restrict,
  num_parcelas    int  not null default 1 check (num_parcelas >= 1),
  criado_em       timestamptz not null default now(),
  -- Coerencia conta x cartao (espelhado no servico criar_despesa).
  constraint despesas_forma_pagamento_chk check (
    (forma_pagamento = 'conta'  and conta_id  is not null and cartao_id is null) or
    (forma_pagamento = 'cartao' and cartao_id is not null and conta_id  is null)
  )
);
create index if not exists despesas_user_data_ix on public.despesas (user_id, data);

-- ───────────────────────────── parcelas ─────────────────────────────
create table if not exists public.parcelas (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  despesa_id  uuid not null references public.despesas(id) on delete cascade,
  fatura_id   uuid references public.faturas(id) on delete restrict,
  numero      int  not null check (numero >= 1),
  valor       numeric(12,2) not null check (valor >= 0),
  vencimento  date,
  criado_em   timestamptz not null default now(),
  unique (despesa_id, numero)
);
create index if not exists parcelas_fatura_ix on public.parcelas (fatura_id);

-- ───────────────────────────── documentos ─────────────────────────────
create table if not exists public.documentos (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  bucket          text not null check (bucket in ('pdfs','imagens')),
  path            text not null,
  fornecedor      text,
  valor_total     numeric(12,2),
  data_documento  date,
  fim_garantia    date,
  tipo_documento  text,   -- nota_fiscal | garantia | recibo | ...
  texto_extraido  text,
  embedding       vector(1536),
  despesa_id      uuid references public.despesas(id) on delete set null,
  criado_em       timestamptz not null default now()
);
-- Busca semantica (decisao 16). HNSW nao exige treino e funciona em tabela vazia.
create index if not exists documentos_embedding_hnsw
  on public.documentos using hnsw (embedding vector_cosine_ops);
create index if not exists documentos_user_garantia_ix
  on public.documentos (user_id, fim_garantia);

-- ─────────────────────────── telegram_codigos ───────────────────────────
-- Vinculo do Telegram por codigo (uso unico, com expiracao) — Passo 6.
create table if not exists public.telegram_codigos (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  codigo     text not null,
  expira_em  timestamptz not null,
  usado      boolean not null default false,
  criado_em  timestamptz not null default now()
);
create index if not exists telegram_codigos_codigo_ix on public.telegram_codigos (codigo);

-- ─────────────────────── telegram_conversas ───────────────────────
-- Historico curto de conversa por chat (continuidade do fluxo de confirmacao).
-- Sem user_id: so o backend (service key) acessa; RLS sem policy bloqueia o resto.
create table if not exists public.telegram_conversas (
  chat_id       bigint primary key,
  historico     jsonb not null default '[]'::jsonb,
  atualizado_em timestamptz not null default now()
);
alter table public.telegram_conversas enable row level security;

-- ═══════════════════════════════ RLS ═══════════════════════════════
-- Policies por dono. profiles usa id; demais usam user_id.

alter table public.profiles enable row level security;
drop policy if exists profiles_select_own on public.profiles;
drop policy if exists profiles_update_own on public.profiles;
create policy profiles_select_own on public.profiles for select using (auth.uid() = id);
create policy profiles_update_own on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

do $$
declare t text;
begin
  foreach t in array array[
    'categorias','subcategorias','locais','contas','cartoes',
    'faturas','despesas','parcelas','documentos','telegram_codigos'
  ]
  loop
    execute format('alter table public.%I enable row level security;', t);
    execute format('drop policy if exists %I on public.%I;', t||'_select_own', t);
    execute format('drop policy if exists %I on public.%I;', t||'_insert_own', t);
    execute format('drop policy if exists %I on public.%I;', t||'_update_own', t);
    execute format('drop policy if exists %I on public.%I;', t||'_delete_own', t);
    execute format('create policy %I on public.%I for select using (auth.uid() = user_id);', t||'_select_own', t);
    execute format('create policy %I on public.%I for insert with check (auth.uid() = user_id);', t||'_insert_own', t);
    execute format('create policy %I on public.%I for update using (auth.uid() = user_id) with check (auth.uid() = user_id);', t||'_update_own', t);
    execute format('create policy %I on public.%I for delete using (auth.uid() = user_id);', t||'_delete_own', t);
  end loop;
end $$;
