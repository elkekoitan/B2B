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

const API_PREFIX = '/api/v1'

function ep(path: string) {
  // ensure single slash between base and prefix, and join path
  return `${API_BASE_URL}${API_PREFIX}${path}`
}

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
    const url = ep(endpoint)
    
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

  // Absolute request (no /api/v1 prefix)
  private async requestAbs<T = any>(
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${path}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    if (this.token) {
      ;(headers as any).Authorization = `Bearer ${this.token}`
    }
    const res = await fetch(url, { ...options, headers })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || data.message || `HTTP ${res.status}`)
    }
    return res.json()
  }

  // Health check
  async healthCheck() {
    // health is at root, not under /api/v1
    return fetch(`${API_BASE_URL}/health`).then(r => r.json())
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

  // RFQ Templates
  async listRFQTemplates() {
    return this.request('/rfqs/templates')
  }
  async getRFQTemplate(category: string) {
    return this.request(`/rfqs/templates/${encodeURIComponent(category)}`)
  }
  async createRFQWithTemplate(payload: any) {
    return this.request('/rfqs/template', {
      method: 'POST',
      body: JSON.stringify(payload),
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
  async orchestrateJob(job: { job_type: string; rfq_id?: string; payload?: any }) {
    const body = { job_type: job.job_type, rfq_id: job.rfq_id, payload: job.payload || {} }
    return this.requestAbs('/orchestrate', { method: 'POST', body: JSON.stringify(body) })
  }

  async getOrchestrateStatus(jobId: string) {
    return this.requestAbs(`/orchestrate/status/${jobId}`)
  }
  async getRecentJobs(params: { limit?: number; job_type?: string } = {}) {
    const qp = new URLSearchParams()
    if (params.limit) qp.append('limit', String(params.limit))
    if (params.job_type) qp.append('job_type', String(params.job_type))
    return this.requestAbs(`/orchestrate/recent${qp.toString() ? `?${qp.toString()}` : ''}`)
  }
  async getJobHistory(params: { limit?: number; job_type?: string } = {}) {
    const qp = new URLSearchParams()
    if (params.limit) qp.append('limit', String(params.limit))
    if (params.job_type) qp.append('job_type', String(params.job_type))
    return this.requestAbs(`/orchestrate/history${qp.toString() ? `?${qp.toString()}` : ''}`)
  }

  async cancelJob(jobId: string) {
    return this.requestAbs(`/orchestrate/${jobId}`, { method: 'DELETE' })
  }

  // Analytics
  async getRFQAnalytics() {
    return this.request('/analytics/rfqs')
  }

  async getJobsAnalytics(days = 7) {
    const qp = new URLSearchParams()
    if (days) qp.append('days', String(days))
    return this.requestAbs(`/analytics/jobs${qp.toString() ? `?${qp.toString()}` : ''}`)
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

  // Catalog
  async getMyCatalog(params: { page?: number; size?: number; search?: string; category?: string; currency?: string } = {}) {
    const qp = new URLSearchParams()
    if (params.page) qp.append('page', String(params.page))
    if (params.size) qp.append('size', String(params.size))
    if (params.search) qp.append('search', String(params.search))
    if (params.category) qp.append('category', String(params.category))
    if (params.currency) qp.append('currency', String(params.currency))
    return this.request(`/catalog/mine${qp.toString() ? `?${qp.toString()}` : ''}`)
  }
  async getCatalogBySupplier(supplierId: string, params: { page?: number; size?: number; search?: string; category?: string; currency?: string } = {}) {
    const qp = new URLSearchParams()
    if (params.page) qp.append('page', String(params.page))
    if (params.size) qp.append('size', String(params.size))
    if (params.search) qp.append('search', String(params.search))
    if (params.category) qp.append('category', String(params.category))
    if (params.currency) qp.append('currency', String(params.currency))
    return this.request(`/catalog/supplier/${supplierId}${qp.toString() ? `?${qp.toString()}` : ''}`)
  }
  async rejectVerification(companyId: string) {
    return this.request('/verification/reject', { method: 'POST', body: JSON.stringify({ company_id: companyId }) })
  }
  async createCatalogItem(item: any) {
    return this.request('/catalog', { method: 'POST', body: JSON.stringify(item) })
  }
  async updateCatalogItem(id: string, updates: any) {
    return this.request(`/catalog/${id}`, { method: 'PUT', body: JSON.stringify(updates) })
  }
  async deleteCatalogItem(id: string) {
    return this.request(`/catalog/${id}`, { method: 'DELETE' })
  }

  // Verification
  async uploadFile(file: File) {
    const form = new FormData()
    form.append('f', file)
    const url = ep('/utils/upload')
    const headers: any = {}
    if (this.token) headers.Authorization = `Bearer ${this.token}`
    const res = await fetch(url, { method: 'POST', headers, body: form as any })
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
    return res.json()
  }
  async requestVerification(payload: any) {
    return this.request('/verification/request', { method: 'POST', body: JSON.stringify(payload) })
  }
  async approveVerification(companyId: string) {
    return this.request('/verification/approve', {
      method: 'POST',
      body: JSON.stringify({ company_id: companyId }),
    })
  }

  async listVerificationRequests(params: { page?: number; size?: number } = {}) {
    const qp = new URLSearchParams()
    if (params.page) qp.append('page', String(params.page))
    if (params.size) qp.append('size', String(params.size))
    return this.request(`/verification/requests${qp.toString() ? `?${qp.toString()}` : ''}`)
  }

  // 2FA
  async setup2FA() {
    return this.request('/auth/2fa/setup', { method: 'POST' })
  }
  async enable2FA(code: string) {
    return this.request('/auth/2fa/enable', { method: 'POST', body: JSON.stringify({ code }) })
  }
  async disable2FA() {
    return this.request('/auth/2fa/disable', { method: 'POST' })
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
