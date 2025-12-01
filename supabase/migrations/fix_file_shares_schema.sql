-- Drop existing table if it exists
DROP TABLE IF EXISTS file_shares CASCADE;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL UNIQUE,
  role VARCHAR(50) NOT NULL CHECK (role IN ('manager', 'hr', 'employee')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create file_shares table with correct schema
CREATE TABLE IF NOT EXISTS file_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_name VARCHAR(255) NOT NULL,
  file_size INTEGER NOT NULL,
  access_code VARCHAR(10) NOT NULL UNIQUE,
  uploaded_by_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  user_role VARCHAR(50) NOT NULL,
  file_path TEXT NOT NULL,
  is_encrypted BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '7 days',
  download_count INTEGER DEFAULT 0
);

-- Create indexes
CREATE INDEX idx_file_shares_access_code ON file_shares(access_code);
CREATE INDEX idx_file_shares_uploaded_by_id ON file_shares(uploaded_by_id);
CREATE INDEX idx_file_shares_created_at ON file_shares(created_at);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_shares ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view their own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- RLS Policies for file_shares table
CREATE POLICY "Users can view their own uploads"
  ON file_shares FOR SELECT
  USING (auth.uid() = uploaded_by_id);

CREATE POLICY "Users can insert their own files"
  ON file_shares FOR INSERT
  WITH CHECK (auth.uid() = uploaded_by_id);

CREATE POLICY "Users can delete their own files"
  ON file_shares FOR DELETE
  USING (auth.uid() = uploaded_by_id);