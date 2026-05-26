-- ═══════════════════════════════════════════════════════════════════════════
--  Vyapar Sarthi Dashboard — Row Level Security (RLS) Policies
--  Run AFTER 01_schema.sql
--  Each user can only read/write their own rows.
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── Enable RLS on all tables ────────────────────────────────────────────────
alter table public.profiles          enable row level security;
alter table public.products          enable row level security;
alter table public.stock_logs        enable row level security;
alter table public.bills             enable row level security;
alter table public.udhar_customers   enable row level security;
alter table public.udhar_transactions enable row level security;
alter table public.sales             enable row level security;
alter table public.imported_files    enable row level security;


-- ─── profiles ────────────────────────────────────────────────────────────────
drop policy if exists "profiles: own row" on public.profiles;
create policy "profiles: own row"
  on public.profiles for all
  using  (auth.uid() = id)
  with check (auth.uid() = id);


-- ─── products ────────────────────────────────────────────────────────────────
drop policy if exists "products: own rows" on public.products;
create policy "products: own rows"
  on public.products for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ─── stock_logs ──────────────────────────────────────────────────────────────
drop policy if exists "stock_logs: own rows" on public.stock_logs;
create policy "stock_logs: own rows"
  on public.stock_logs for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ─── bills ───────────────────────────────────────────────────────────────────
drop policy if exists "bills: own rows" on public.bills;
create policy "bills: own rows"
  on public.bills for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ─── udhar_customers ─────────────────────────────────────────────────────────
drop policy if exists "udhar_customers: own rows" on public.udhar_customers;
create policy "udhar_customers: own rows"
  on public.udhar_customers for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ─── udhar_transactions ──────────────────────────────────────────────────────
drop policy if exists "udhar_transactions: own rows" on public.udhar_transactions;
create policy "udhar_transactions: own rows"
  on public.udhar_transactions for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ─── sales ───────────────────────────────────────────────────────────────────
drop policy if exists "sales: own rows" on public.sales;
create policy "sales: own rows"
  on public.sales for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ─── imported_files ──────────────────────────────────────────────────────────
drop policy if exists "imported_files: own rows" on public.imported_files;
create policy "imported_files: own rows"
  on public.imported_files for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);
