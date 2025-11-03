export interface FileShare {
  id: string;
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
  share_code: string;
  sender_name: string;
  downloads: number;
  max_downloads: number | null;
  expires_at: string | null;
  created_at: string;
}
