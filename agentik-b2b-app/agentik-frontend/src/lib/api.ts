// API client for Agentik B2B backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  setToken(token: string | null) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Network error' }))
        throw new Error(error.message || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Auth endpoints
  async register(userData: any) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  async getProfile() {
    return this.request('/api/v1/auth/profile')
  }

  async updateProfile(data: any) {
    return this.request('/api/v1/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  // RFQ endpoints
  async getRFQs(params: any = {}) {
    const searchParams = new URLSearchParams(params)
    return this.request(`/api/v1/rfqs?${searchParams}`)
  }

  async getRFQ(id: string) {
    return this.request(`/api/v1/rfqs/${id}`)
  }

  async createRFQ(data: any) {
    return this.request('/api/v1/rfqs', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateRFQ(id: string, data: any) {
    return this.request(`/api/v1/rfqs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  // Supplier endpoints
  async getSuppliers(params: any = {}) {
    const searchParams = new URLSearchParams(params)
    return this.request(`/api/v1/suppliers?${searchParams}`)
  }

  async getSupplier(id: string) {
    return this.request(`/api/v1/suppliers/${id}`)
  }

  async createSupplierProfile(data: any) {
    return this.request('/api/v1/suppliers/profile', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateSupplierProfile(data: any) {
    return this.request('/api/v1/suppliers/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async getSupplierProfile() {
    return this.request('/api/v1/suppliers/profile')
  }

  // Offer endpoints
  async getOffers(params: any = {}) {
    const searchParams = new URLSearchParams(params)
    return this.request(`/api/v1/offers?${searchParams}`)
  }

  async getOffer(id: string) {
    return this.request(`/api/v1/offers/${id}`)
  }

  async createOffer(data: any) {
    return this.request('/api/v1/offers', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateOffer(id: string, data: any) {
    return this.request(`/api/v1/offers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  // Notification endpoints
  async getNotifications(params: any = {}) {
    const searchParams = new URLSearchParams(params)
    return this.request(`/api/v1/notifications?${searchParams}`)
  }

  async markNotificationRead(id: string) {
    return this.request(`/api/v1/notifications/${id}/read`, {
      method: 'PUT'
    })
  }

  async markAllNotificationsRead() {
    return this.request('/api/v1/notifications/mark-all-read', {
      method: 'PUT'
    })
  }

  async getUnreadCount() {
    return this.request('/api/v1/notifications/unread-count')
  }
}

export const apiClient = new ApiClient(API_BASE_URL)