import { createClient } from '@supabase/supabase-js'

const supabaseUrl =
  import.meta.env.VITE_SUPABASE_URL ||
  // CRA-style fallback
  (import.meta as any).env?.REACT_APP_SUPABASE_URL ||
  'https://your-project.supabase.co'

const supabaseAnonKey =
  import.meta.env.VITE_SUPABASE_ANON_KEY ||
  // CRA-style fallback
  (import.meta as any).env?.REACT_APP_SUPABASE_ANON_KEY ||
  'your-anon-key'

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
})

// Database types
export interface User {
  id: string
  email: string
  full_name?: string
  company_name?: string
  phone?: string
  is_admin?: boolean
  created_at: string
  updated_at?: string
}

export interface RFQ {
  id: string
  title: string
  description: string
  category: string
  quantity: number
  unit: string
  budget_min?: number
  budget_max?: number
  deadline: string
  delivery_location: string
  requirements?: string
  status: 'draft' | 'published' | 'in_progress' | 'completed' | 'cancelled'
  urgency?: 'low' | 'medium' | 'high'
  user_id: string
  created_at: string
  updated_at?: string
}

export interface Supplier {
  id: string
  name: string
  email: string
  phone?: string
  company: string
  address?: string
  website?: string
  categories: string[]
  description?: string
  verified: boolean
  rating?: number
  created_at: string
  updated_at?: string
}

export interface Offer {
  id: string
  rfq_id: string
  supplier_id: string
  unit_price: number
  total_price: number
  delivery_time: number
  terms?: string
  notes?: string
  status: 'pending' | 'submitted' | 'accepted' | 'rejected'
  submitted_at: string
  updated_at?: string
  verification_score?: number
  verified?: boolean
}

export interface JobStatus {
  job_id: string
  status: 'queued' | 'in_progress' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
  result?: any
  error?: string
}
