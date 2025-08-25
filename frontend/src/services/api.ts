// Prefer explicit env value; otherwise derive from current host (port 18000)
const API_BASE_URL = (() => {
  const envUrl =
    import.meta.env.VITE_API_URL ||
    (import.meta as any).env?.REACT_APP_BACKEND_URL ||
    ''
  if (envUrl) return envUrl
  try {
    const host = window?.location?.hostname || 'localhost'
    return `http://${host}:18000`
  } catch {
    return 'http://localhost:8000'
  }
})()

interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  errors?: string[]
  total?: number
  page?: number
  per_page?: number
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor() {
    this.baseUrl = API_BASE_URL
  }

  setToken(token: string | null) {
    this.token = token
  }

  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health')
  }

  // RFQ endpoints
  async getRFQs(params: {
    page?: number
    per_page?: number
    status?: string
    category?: string
  } = {}) {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value))
      }
    })
    
    const endpoint = `/rfqs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return this.request(endpoint)
  }

  async getRFQ(id: string) {
    return this.request(`/rfqs/${id}`)
  }

  async createRFQ(rfqData: any) {
    return this.request('/rfqs', {
      method: 'POST',
      body: JSON.stringify(rfqData),
    })
  }

  async updateRFQ(id: string, updates: any) {
    return this.request(`/rfqs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    })
  }

  async deleteRFQ(id: string) {
    return this.request(`/rfqs/${id}`, {
      method: 'DELETE',
    })
  }

  // Supplier endpoints
  async getSuppliers(params: {
    page?: number
    per_page?: number
    category?: string
    verified_only?: boolean
  } = {}) {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value))
      }
    })
    
    const endpoint = `/suppliers${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return this.request(endpoint)
  }

  async createSupplier(supplierData: any) {
    return this.request('/suppliers', {
      method: 'POST',
      body: JSON.stringify(supplierData),
    })
  }

  // Offer endpoints
  async getOffers(rfqId?: string) {
    const endpoint = rfqId ? `/offers?rfq_id=${rfqId}` : '/offers'
    return this.request(endpoint)
  }

  async getOffersByRFQ(rfqId: string) {
    return this.request(`/offers/by-rfq/${rfqId}`)
  }

  // Agent orchestration
  async startWorkflow(jobData: {
    job_type: string
    rfq_id: string
    payload?: any
  }) {
    return this.request('/orchestrate', {
      method: 'POST',
      body: JSON.stringify(jobData),
    })
  }

  async getJobStatus(jobId: string) {
    return this.request(`/status/${jobId}`)
  }

  // Analytics
  async getRFQAnalytics() {
    return this.request('/analytics/rfqs')
  }

  // Admin endpoints
  async adminGetAllRFQs(params: {
    page?: number
    per_page?: number
  } = {}) {
    const queryParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value))
      }
    })
    
    const endpoint = `/admin/rfqs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return this.request(endpoint)
  }
}

export const apiClient = new ApiClient()

// Hook to use API with authentication
import { useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

export function useApiClient() {
  const { session } = useAuth()

  useEffect(() => {
    apiClient.setToken(session?.access_token || null)
  }, [session?.access_token])

  return apiClient
}
