-- ═══════════════════════════════════════════════════════════════════════════
--  Vyapar Sarthi Dashboard — New Features Schema
--  Run this in Supabase → SQL Editor
--  Order: run AFTER 01_schema.sql and 02_rls.sql
--  Tables: referral_codes, referrals, dukandar_relationships,
--          admin_users, support_tickets, admin_notifications, user_notifications
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── 1. REFERRAL CODES ─────────────────────────────────────────────────────────
-- Each user gets one unique referral code they can share
create table if not exists public.referral_codes (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references auth.users(id) on delete cascade,
  code                text not null unique,
  total_referrals     integer not null default 0,
  successful_referrals integer not null default 0,
  created_at          timestamptz not null default now(),
  unique(user_id)
);

create index if not exists referral_codes_user_id_idx on public.referral_codes(user_id);
create index if not exists referral_codes_code_idx    on public.referral_codes(code);


-- ─── 2. REFERRALS ──────────────────────────────────────────────────────────────
-- Tracks who referred whom and the reward status
create table if not exists public.referrals (
  id                uuid primary key default gen_random_uuid(),
  referrer_id       uuid not null references auth.users(id) on delete cascade,
  referred_id       uuid references auth.users(id) on delete set null,
  referral_code     text not null,
  referred_email    text,
  status            text not null default 'pending' check (status in ('pending','completed','expired')),
  discount_applied  boolean not null default false,
  referrer_rewarded boolean not null default false,
  created_at        timestamptz not null default now(),
  completed_at      timestamptz
);

create index if not exists referrals_referrer_id_idx on public.referrals(referrer_id);
create index if not exists referrals_referred_id_idx on public.referrals(referred_id);
create index if not exists referrals_code_idx        on public.referrals(referral_code);


-- ─── 3. DUKANDAR RELATIONSHIPS ─────────────────────────────────────────────────
-- Links wholesalers (business plan) to their retailers/dukandar
create table if not exists public.dukandar_relationships (
  id             uuid primary key default gen_random_uuid(),
  wholesaler_id  uuid not null references auth.users(id) on delete cascade,
  retailer_id    uuid not null references auth.users(id) on delete cascade,
  status         text not null default 'active' check (status in ('active','inactive')),
  created_at     timestamptz not null default now(),
  unique(wholesaler_id, retailer_id)
);

create index if not exists dukandar_wholesaler_idx on public.dukandar_relationships(wholesaler_id);
create index if not exists dukandar_retailer_idx   on public.dukandar_relationships(retailer_id);


-- ─── 4. ADMIN USERS ────────────────────────────────────────────────────────────
-- Separate admin accounts for managing the platform
create table if not exists public.admin_users (
  id              uuid primary key default gen_random_uuid(),
  email           text not null unique,
  hashed_password text not null,
  full_name       text not null,
  role            text not null default 'admin' check (role in ('superadmin','admin','support')),
  is_active       integer not null default 1,
  created_at      timestamptz not null default now()
);

create index if not exists admin_users_email_idx on public.admin_users(email);


-- ─── 5. SUPPORT TICKETS ────────────────────────────────────────────────────────
-- User-submitted support requests and complaints
create table if not exists public.support_tickets (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references auth.users(id) on delete set null,
  name        text not null,
  email       text not null,
  phone       text,
  shop_name   text,
  type        text not null check (type in ('Issue','Complaint','Refund','Inquiry','Suggestion')),
  priority    text not null default 'normal' check (priority in ('low','normal','high','urgent')),
  subject     text,
  message     text not null,
  status      text not null default 'open' check (status in ('open','in_progress','resolved','closed')),
  admin_notes text,
  refund_amount text,
  refund_reason text,
  txn_id        text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  resolved_at timestamptz
);

-- Add refund columns to existing tables (safe to run multiple times)
alter table public.support_tickets add column if not exists refund_amount text;
alter table public.support_tickets add column if not exists refund_reason text;
alter table public.support_tickets add column if not exists txn_id text;

create index if not exists tickets_user_id_idx on public.support_tickets(user_id);
create index if not exists tickets_status_idx  on public.support_tickets(status);


-- ─── 6. ADMIN BROADCAST NOTIFICATIONS ──────────────────────────────────────────
-- Notifications created by admins to broadcast to users
create table if not exists public.admin_notifications (
  id                uuid primary key default gen_random_uuid(),
  admin_id          uuid not null references public.admin_users(id) on delete cascade,
  title             text not null,
  message           text not null,
  notification_type text not null default 'broadcast' check (notification_type in ('broadcast','update','alert','promotional')),
  target_audience   text not null default 'all' check (target_audience in ('all','specific_plan','specific_user')),
  target_plan       text,
  created_at        timestamptz not null default now()
);

create index if not exists admin_notif_admin_idx on public.admin_notifications(admin_id);


-- ─── 7. USER IN-APP NOTIFICATIONS ──────────────────────────────────────────────
-- Delivered notifications visible inside the app dashboard
create table if not exists public.user_notifications (
  id                    uuid primary key default gen_random_uuid(),
  user_id               uuid not null references auth.users(id) on delete cascade,
  admin_notification_id uuid references public.admin_notifications(id) on delete set null,
  title                 text not null,
  message               text not null,
  notification_type     text not null default 'info' check (notification_type in ('info','warning','expiry','promotion','system')),
  is_read               boolean not null default false,
  link                  text,
  created_at            timestamptz not null default now()
);

create index if not exists user_notif_user_id_idx  on public.user_notifications(user_id);
create index if not exists user_notif_read_idx     on public.user_notifications(user_id, is_read);
create index if not exists user_notif_created_idx  on public.user_notifications(user_id, created_at desc);


-- ═══════════════════════════════════════════════════════════════════════════
--  ROW LEVEL SECURITY (RLS) POLICIES
-- ═══════════════════════════════════════════════════════════════════════════

alter table public.referral_codes        enable row level security;
alter table public.referrals             enable row level security;
alter table public.dukandar_relationships enable row level security;
alter table public.admin_users           enable row level security;
alter table public.support_tickets       enable row level security;
alter table public.admin_notifications   enable row level security;
alter table public.user_notifications    enable row level security;

-- ─── Referral Codes: user sees only their own ───────────────────────────────
drop policy if exists "referral_codes: own row" on public.referral_codes;
create policy "referral_codes: own row"
  on public.referral_codes for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ─── Referrals: referrer sees their outgoing, referred sees incoming ────────
drop policy if exists "referrals: user access" on public.referrals;
create policy "referrals: user access"
  on public.referrals for select
  using  (auth.uid() = referrer_id or auth.uid() = referred_id);

drop policy if exists "referrals: insert" on public.referrals;
create policy "referrals: insert"
  on public.referrals for insert
  with check (auth.uid() = referrer_id);

-- ─── Dukandar: wholesaler reads their dukandar, retailer sees their wholesaler
drop policy if exists "dukandar: wholesaler access" on public.dukandar_relationships;
create policy "dukandar: wholesaler access"
  on public.dukandar_relationships for select
  using  (auth.uid() = wholesaler_id or auth.uid() = retailer_id);

drop policy if exists "dukandar: wholesaler insert" on public.dukandar_relationships;
create policy "dukandar: wholesaler insert"
  on public.dukandar_relationships for insert
  with check (auth.uid() = wholesaler_id);

-- ─── Admin Users: only existing admins can read/write ───────────────────────
-- First admin must be inserted via the seed below or directly in Supabase dashboard.
-- After that, admins can manage other admins.
drop policy if exists "admin_users: select" on public.admin_users;
create policy "admin_users: select"
  on public.admin_users for select
  using  (auth.uid() in (select id from public.admin_users where is_active = 1));

drop policy if exists "admin_users: insert" on public.admin_users;
create policy "admin_users: insert"
  on public.admin_users for insert
  with check (auth.uid() in (select id from public.admin_users where is_active = 1));

drop policy if exists "admin_users: update" on public.admin_users;
create policy "admin_users: update"
  on public.admin_users for update
  using  (auth.uid() in (select id from public.admin_users where is_active = 1))
  with check (auth.uid() in (select id from public.admin_users where is_active = 1));

drop policy if exists "admin_users: delete" on public.admin_users;
create policy "admin_users: delete"
  on public.admin_users for delete
  using  (auth.uid() in (select id from public.admin_users where is_active = 1));

-- ─── Support Tickets: users see their own, admins see all ───────────────────
drop policy if exists "tickets: user access" on public.support_tickets;
create policy "tickets: user access"
  on public.support_tickets for select
  using  (auth.uid() = user_id or auth.uid() in (select id from public.admin_users where is_active = 1));

drop policy if exists "tickets: user insert" on public.support_tickets;
create policy "tickets: user insert"
  on public.support_tickets for insert
  with check (auth.uid() = user_id or auth.uid() is null);

drop policy if exists "tickets: admin update" on public.support_tickets;
create policy "tickets: admin update"
  on public.support_tickets for update
  using  (auth.uid() in (select id from public.admin_users where is_active = 1))
  with check (auth.uid() in (select id from public.admin_users where is_active = 1));

-- ─── Admin Notifications: only admins can write ────────────────────────────
drop policy if exists "admin_notifications: read all" on public.admin_notifications;
create policy "admin_notifications: read all"
  on public.admin_notifications for select
  using  (true);

drop policy if exists "admin_notifications: admin write" on public.admin_notifications;
create policy "admin_notifications: admin write"
  on public.admin_notifications for insert
  with check (auth.uid() in (select id from public.admin_users where is_active = 1));

-- ─── User Notifications: user sees only their own ──────────────────────────
drop policy if exists "user_notifications: own rows" on public.user_notifications;
create policy "user_notifications: own rows"
  on public.user_notifications for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);


-- ═══════════════════════════════════════════════════════════════════════════
--  HELPER FUNCTION & TRIGGER: AUTO-UPDATE updated_at
-- ═══════════════════════════════════════════════════════════════════════════

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_support_tickets_updated_at on public.support_tickets;
create trigger set_support_tickets_updated_at
  before update on public.support_tickets
  for each row execute function public.set_updated_at();


-- ═══════════════════════════════════════════════════════════════════════════
--  SEED: Create a default admin user
--  ⚠️ CHANGE THE PASSWORD AFTER FIRST LOGIN
-- ═══════════════════════════════════════════════════════════════════════════

-- Generate a bcrypt hash for your admin password first.
-- Run this in your terminal:
--   node -e "console.log(require('crypto').randomBytes(16).toString('hex'))"
-- Or use: https://bcrypt.online/ to generate a hash for e.g. "admin123"
--
-- Then insert the admin user (replace the hash below with your generated one):
-- insert into public.admin_users (email, hashed_password, full_name, role)
-- values (
--   'admin@vyaparsarthi.com',
--   '<your-bcrypt-hash>',
--   'Super Admin',
--   'superadmin'
-- )
-- on conflict (email) do nothing;
