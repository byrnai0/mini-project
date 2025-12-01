export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          role: 'manager' | 'hr' | 'employee'
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          role: 'manager' | 'hr' | 'employee'
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          role?: 'manager' | 'hr' | 'employee'
          created_at?: string
          updated_at?: string
        }
      }
      file_shares: {
        Row: {
          id: string
          file_name: string
          file_size: number
          access_code: string
          uploaded_by_id: string
          user_role: string
          file_path: string
          is_encrypted: boolean
          created_at: string
          expires_at: string
          download_count: number
        }
        Insert: {
          id?: string
          file_name: string
          file_size: number
          access_code: string
          uploaded_by_id: string
          user_role: string
          file_path: string
          is_encrypted?: boolean
          created_at?: string
          expires_at?: string
          download_count?: number
        }
        Update: {
          id?: string
          file_name?: string
          file_size?: number
          access_code?: string
          uploaded_by_id?: string
          user_role?: string
          file_path?: string
          is_encrypted?: boolean
          created_at?: string
          expires_at?: string
          download_count?: number
        }
      }
    }
    Views: {}
    Functions: {
      generate_access_code: {
        Args: Record<string, never>
        Returns: string
      }
    }
    Enums: {}
  }
}