
-- ═══════════════════════════════════════════════════════════════════════════
--  Vyapar Sarthi Dashboard — Storage Setup
--  Run this in Supabase → SQL Editor to enable PDF Bill sharing
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Create the 'invoices' bucket
insert into storage.buckets (id, name, public)
values ('invoices', 'invoices', true)
on conflict (id) do nothing;

-- 2. Allow public access to read files (so customers can view their bills)
create policy "Public Access to Invoices"
  on storage.objects for select
  using ( bucket_id = 'invoices' );

-- 3. Allow authenticated users to upload their own invoices
-- We use a simple policy for now: anyone with an account can upload
create policy "Users can upload invoices"
  on storage.objects for insert
  with check ( 
    bucket_id = 'invoices' 
    AND auth.role() = 'authenticated'
  );

-- 4. Allow users to update/delete their own files (optional)
create policy "Users can manage their own invoices"
  on storage.objects for all
  using ( 
    bucket_id = 'invoices' 
    AND auth.role() = 'authenticated'
  );
