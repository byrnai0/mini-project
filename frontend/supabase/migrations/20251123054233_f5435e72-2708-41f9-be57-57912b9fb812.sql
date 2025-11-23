-- Create storage bucket for shared files
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('shared-files', 'shared-files', false, 104857600, null);

-- Create table to track file shares
create table public.file_shares (
  id uuid primary key default gen_random_uuid(),
  file_path text not null,
  file_name text not null,
  file_size bigint not null,
  access_code text unique not null,
  created_at timestamp with time zone default now(),
  expires_at timestamp with time zone default (now() + interval '7 days'),
  download_count integer default 0
);

-- Enable RLS
alter table public.file_shares enable row level security;

-- Allow anyone to read file shares (needed for downloads)
create policy "Anyone can view file shares"
  on public.file_shares
  for select
  using (true);

-- Allow anyone to insert file shares (for uploads)
create policy "Anyone can create file shares"
  on public.file_shares
  for insert
  with check (true);

-- Storage policies for shared files bucket
create policy "Anyone can upload files"
  on storage.objects
  for insert
  with check (bucket_id = 'shared-files');

create policy "Anyone can view shared files"
  on storage.objects
  for select
  using (bucket_id = 'shared-files');

-- Function to generate unique access code
create or replace function generate_access_code()
returns text
language plpgsql
as $$
declare
  chars text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  result text := '';
  i integer;
begin
  for i in 1..6 loop
    result := result || substr(chars, floor(random() * length(chars) + 1)::integer, 1);
  end loop;
  return result;
end;
$$;

-- Create index for faster lookups
create index idx_file_shares_access_code on public.file_shares(access_code);
create index idx_file_shares_expires_at on public.file_shares(expires_at);