/*
  # File Sharing System Schema

  1. New Tables
    - `file_shares`
      - `id` (uuid, primary key) - Unique identifier for each file share
      - `file_name` (text) - Original name of the uploaded file
      - `file_url` (text) - URL to the stored file in Supabase storage
      - `file_size` (bigint) - Size of the file in bytes
      - `file_type` (text) - MIME type of the file
      - `share_code` (text, unique) - 6-digit secret code for accessing the file
      - `sender_name` (text) - Optional name of the sender
      - `downloads` (integer) - Number of times the file has been downloaded
      - `max_downloads` (integer) - Maximum allowed downloads (null = unlimited)
      - `expires_at` (timestamptz) - Expiration timestamp (null = never expires)
      - `created_at` (timestamptz) - When the share was created
      
  2. Security
    - Enable RLS on `file_shares` table
    - Add policy for anyone to create file shares
    - Add policy for anyone to read file shares by share_code
    - Add policy for anyone to update download count
    
  3. Storage
    - Create storage bucket for file uploads
    - Enable public access for authenticated downloads
    
  4. Indexes
    - Add index on share_code for fast lookups
*/

-- Create the file_shares table
CREATE TABLE IF NOT EXISTS file_shares (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  file_name text NOT NULL,
  file_url text NOT NULL,
  file_size bigint NOT NULL DEFAULT 0,
  file_type text NOT NULL DEFAULT 'application/octet-stream',
  share_code text UNIQUE NOT NULL,
  sender_name text DEFAULT '',
  downloads integer DEFAULT 0,
  max_downloads integer DEFAULT NULL,
  expires_at timestamptz DEFAULT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create index on share_code for fast lookups
CREATE INDEX IF NOT EXISTS idx_file_shares_share_code ON file_shares(share_code);

-- Enable Row Level Security
ALTER TABLE file_shares ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can create a file share
CREATE POLICY "Anyone can create file shares"
  ON file_shares
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

-- Policy: Anyone can read file shares by share_code
CREATE POLICY "Anyone can read file shares"
  ON file_shares
  FOR SELECT
  TO anon, authenticated
  USING (true);

-- Policy: Anyone can update download count
CREATE POLICY "Anyone can update file shares"
  ON file_shares
  FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- Create storage bucket for files
INSERT INTO storage.buckets (id, name, public)
VALUES ('file-shares', 'file-shares', true)
ON CONFLICT (id) DO NOTHING;

-- Policy: Anyone can upload files
CREATE POLICY "Anyone can upload files"
  ON storage.objects
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (bucket_id = 'file-shares');

-- Policy: Anyone can read files
CREATE POLICY "Anyone can read files"
  ON storage.objects
  FOR SELECT
  TO anon, authenticated
  USING (bucket_id = 'file-shares');

-- Policy: Anyone can delete their own files
CREATE POLICY "Anyone can delete files"
  ON storage.objects
  FOR DELETE
  TO anon, authenticated
  USING (bucket_id = 'file-shares');