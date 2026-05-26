-- ═══════════════════════════════════════════════════════════════════════════
--  Vyapar Sarthi Dashboard — Database Schema
--  Run this file first in Supabase → SQL Editor
--  Order: 01_schema.sql → 02_rls.sql
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── Extensions ──────────────────────────────────────────────────────────────
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";


-- ─── 1. PROFILES ─────────────────────────────────────────────────────────────
create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  store_name   text not null default 'My Store',
  owner_name   text not null default '',
  mobile       text not null default '',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

-- Auto-create profile when a new user signs up
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, store_name, owner_name, mobile)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'store_name', 'My Store'),
    coalesce(new.raw_user_meta_data->>'full_name',  ''),
    coalesce(new.raw_user_meta_data->>'mobile',     '')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();


-- ─── 2. PRODUCTS (Stock / Inventory) ─────────────────────────────────────────
create table if not exists public.products (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  name           text not null,
  category       text not null default 'General',
  stock          numeric(12,3) not null default 0,
  min_stock      numeric(12,3) not null default 0,
  mrp            numeric(10,2) not null default 0,
  selling_price  numeric(10,2) not null default 0,
  cost           numeric(10,2) not null default 0,
  unit           text not null default 'pcs',
  barcode        text,
  archived       boolean not null default false,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create index if not exists products_user_id_idx on public.products(user_id);
create index if not exists products_barcode_idx  on public.products(barcode) where barcode is not null;


-- ─── 3. STOCK LOGS ───────────────────────────────────────────────────────────
create table if not exists public.stock_logs (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  product_id    uuid references public.products(id) on delete set null,
  product_name  text not null,
  type          text not null check (type in ('add','remove','sale','import','adjust')),
  quantity      numeric(12,3) not null,
  note          text,
  date          date not null default current_date,
  created_at    timestamptz not null default now()
);

create index if not exists stock_logs_user_id_idx    on public.stock_logs(user_id);
create index if not exists stock_logs_product_id_idx on public.stock_logs(product_id);
create index if not exists stock_logs_date_idx       on public.stock_logs(date desc);


-- ─── 4. BILLS ────────────────────────────────────────────────────────────────
create table if not exists public.bills (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid not null references auth.users(id) on delete cascade,
  bill_number      text not null,
  customer_name    text,
  items            jsonb not null default '[]',
  subtotal         numeric(10,2) not null default 0,
  discount         numeric(10,2) not null default 0,
  total            numeric(10,2) not null default 0,
  amount_paid      numeric(10,2) not null default 0,
  remaining_amount numeric(10,2) not null default 0,
  payment_method   text not null default 'cash',
  date             date not null default current_date,
  created_at       timestamptz not null default now()
);

create index if not exists bills_user_id_idx  on public.bills(user_id);
create index if not exists bills_date_idx     on public.bills(date desc);
create index if not exists bills_customer_idx on public.bills(customer_name) where customer_name is not null;


-- ─── 5. UDHAR CUSTOMERS ──────────────────────────────────────────────────────
create table if not exists public.udhar_customers (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  name       text not null,
  mobile     text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, name)
);

create index if not exists udhar_customers_user_id_idx on public.udhar_customers(user_id);


-- ─── 6. UDHAR TRANSACTIONS ───────────────────────────────────────────────────
create table if not exists public.udhar_transactions (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  customer_id uuid not null references public.udhar_customers(id) on delete cascade,
  type        text not null check (type in ('udhar','payment')),
  amount      numeric(10,2) not null,
  note        text,
  bill_number text,
  date        date not null default current_date,
  created_at  timestamptz not null default now()
);

create index if not exists udhar_tx_user_id_idx     on public.udhar_transactions(user_id);
create index if not exists udhar_tx_customer_id_idx on public.udhar_transactions(customer_id);
create index if not exists udhar_tx_date_idx        on public.udhar_transactions(date desc);


-- ─── 7. SALES ────────────────────────────────────────────────────────────────
create table if not exists public.sales (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  date           date not null default current_date,
  total_amount   numeric(10,2) not null default 0,
  payment_method text not null default 'cash',
  note           text,
  bill_id        uuid references public.bills(id) on delete set null,
  created_at     timestamptz not null default now()
);

create index if not exists sales_user_id_idx on public.sales(user_id);
create index if not exists sales_date_idx    on public.sales(date desc);


-- ─── 8. IMPORTED FILES ───────────────────────────────────────────────────────
create table if not exists public.imported_files (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  file_name       text not null,
  data_type       text not null default 'unknown',
  summary         text,
  raw_text        text,
  khata_entries   jsonb not null default '[]',
  stock_entries   jsonb not null default '[]',
  sales_entries   jsonb not null default '[]',
  merged_sections jsonb not null default '[]',
  merged_date     date,
  created_at      timestamptz not null default now()
);

create index if not exists imported_files_user_id_idx on public.imported_files(user_id);


-- ─── Helper: auto-update updated_at ──────────────────────────────────────────
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_profiles_updated_at          on public.profiles;
drop trigger if exists set_products_updated_at          on public.products;
drop trigger if exists set_udhar_customers_updated_at   on public.udhar_customers;

create trigger set_profiles_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

create trigger set_products_updated_at
  before update on public.products
  for each row execute function public.set_updated_at();

create trigger set_udhar_customers_updated_at
  before update on public.udhar_customers
  for each row execute function public.set_updated_at();
