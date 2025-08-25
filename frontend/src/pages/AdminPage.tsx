import React, { useState, useEffect } from 'react'
import { useApiClient } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { LoadingSpinner } from '../components/LoadingSpinner'
import {
  Shield,
  Users,
  FileText,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Search,
  Plus,
  Eye,
  RefreshCw,
  BarChart3,
  Activity
} from 'lucide-react'
import type { RFQ, Supplier } from '../lib/supabase'

interface AdminStats {
  total_users: number
  total_rfqs: number
  total_suppliers: number
  active_workflows: number
  completed_workflows: number
  system_health: 'healthy' | 'warning' | 'critical'
}

export function AdminPage() {
  const apiClient = useApiClient()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'rfqs' | 'suppliers' | 'system'>('overview')
  
  // Overview data
  const [stats, setStats] = useState<AdminStats | null>(null)
  
  // RFQs data
  const [rfqs, setRfqs] = useState<RFQ[]>([])
  const [rfqsPage, setRfqsPage] = useState(1)
  const [rfqsTotal, setRfqsTotal] = useState(0)
  
  // Suppliers data
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [suppliersPage, setSuppliersPage] = useState(1)
  const [suppliersTotal, setSuppliersTotal] = useState(0)
  
  // Search and filter
  const [searchTerm, setSearchTerm] = useState('')
  const [error, setError] = useState('')

  const loadOverviewData = async () => {
    try {
      // In a real implementation, there would be admin-specific endpoints
      // For now, we'll simulate admin stats
      const mockStats: AdminStats = {
        total_users: 45,
        total_rfqs: 128,
        total_suppliers: 89,
        active_workflows: 12,
        completed_workflows: 67,
        system_health: 'healthy'
      }
      setStats(mockStats)
    } catch (error) {
      console.error('Failed to load overview data:', error)
    }
  }

  const loadRFQs = async () => {
    try {
      const response = await apiClient.adminGetAllRFQs({
        page: rfqsPage,
        per_page: 20
      })
      
      if (response.success) {
        setRfqs(response.data || [])
        setRfqsTotal(response.total || 0)
      }
    } catch (error: any) {
      setError('RFQ verileri yüklenirken hata oluştu')
    }
  }

  const loadSuppliers = async () => {
    try {
      const response = await apiClient.getSuppliers({
        page: suppliersPage,
        per_page: 20
      })
      
      if (response.success) {
        setSuppliers(response.data || [])
        setSuppliersTotal(response.total || 0)
      }
    } catch (error: any) {
      setError('Tedarikçi verileri yüklenirken hata oluştu')
    }
  }

  const loadData = async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true)
      else setLoading(true)
      setError('')

      await loadOverviewData()
      
      if (activeTab === 'rfqs') {
        await loadRFQs()
      } else if (activeTab === 'suppliers') {
        await loadSuppliers()
      }
    } catch (error) {
      console.error('Data loading failed:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [activeTab, rfqsPage, suppliersPage])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getHealthBadge = (health: string) => {
    const colors = {
      healthy: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800'
    }
    
    const texts = {
      healthy: 'Sağlıklı',
      warning: 'Uyarı',
      critical: 'Kritik'
    }
    
    const colorClass = colors[health as keyof typeof colors] || colors.healthy
    const text = texts[health as keyof typeof texts] || health
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {text}
      </span>
    )
  }

  if (loading && !stats) {
    return <LoadingSpinner />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Shield className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
              <p className="text-gray-600">Sistem yönetimi ve özetler</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {stats && getHealthBadge(stats.system_health)}
            <Button
              variant="outline"
              onClick={() => loadData(true)}
              disabled={refreshing}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Yenile
            </Button>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 mb-6 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-white rounded-lg p-1">
          {[
            { key: 'overview', label: 'Genel Bakış', icon: BarChart3 },
            { key: 'rfqs', label: 'Tüm RFQ\'lar', icon: FileText },
            { key: 'suppliers', label: 'Tedarikçiler', icon: Users },
            { key: 'system', label: 'Sistem', icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Users className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Toplam Kullanıcı</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-indigo-100 rounded-lg">
                      <FileText className="h-6 w-6 text-indigo-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Toplam RFQ</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.total_rfqs}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Users className="h-6 w-6 text-green-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Tedarikçiler</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.total_suppliers}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <TrendingUp className="h-6 w-6 text-yellow-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Aktif Workflow</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.active_workflows}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Son Aktiviteler</CardTitle>
                <CardDescription>
                  Sistemdeki son işlemler ve etkinlikler
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-3 bg-blue-50 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-blue-600" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Yeni RFQ oluşturuldu</p>
                      <p className="text-xs text-gray-600">"Elektronik Komponent Tedariki" - 15 dakika önce</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 p-3 bg-green-50 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Workflow tamamlandı</p>
                      <p className="text-xs text-gray-600">RFQ ID: abc12345 - 32 dakika önce</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 p-3 bg-yellow-50 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Yeni tedarikçi kaydı</p>
                      <p className="text-xs text-gray-600">"Global Electronics Ltd." - 1 saat önce</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* RFQs Tab */}
        {activeTab === 'rfqs' && (
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Tüm RFQ'lar ({rfqsTotal})</CardTitle>
                  <CardDescription>Sistemdeki tüm teklif talepleri</CardDescription>
                </div>
              </div>
              
              <div className="flex gap-4 mt-4">
                <div className="relative flex-1">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <Input
                    placeholder="RFQ ara..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {rfqs.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">RFQ bulunamadı</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {rfqs.map((rfq) => (
                    <div key={rfq.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-medium text-gray-900">{rfq.title}</h3>
                        <span className="text-xs text-gray-500">
                          {formatDate(rfq.created_at)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{rfq.description}</p>
                      <div className="flex justify-between items-center text-sm text-gray-600">
                        <span>Kullanıcı: {rfq.user_id.slice(-8)}</span>
                        <span className="capitalize">Durum: {rfq.status}</span>
                        <span>{rfq.quantity} {rfq.unit}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Suppliers Tab */}
        {activeTab === 'suppliers' && (
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Tedarikçiler ({suppliersTotal})</CardTitle>
                  <CardDescription>Sistemdeki tedarikçiler</CardDescription>
                </div>
                <Button className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Yeni Tedarikçi
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {suppliers.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">Tedarikçi bulunamadı</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {suppliers.map((supplier) => (
                    <div key={supplier.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-medium text-gray-900">{supplier.name}</h3>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          supplier.verified ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {supplier.verified ? 'Doğrulanmış' : 'Beklemede'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{supplier.company}</p>
                      <p className="text-sm text-gray-600 mb-3">{supplier.email}</p>
                      <div className="flex flex-wrap gap-1">
                        {supplier.categories.map((category, index) => (
                          <span
                            key={index}
                            className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                          >
                            {category}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* System Tab */}
        {activeTab === 'system' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Sistem Sağlığı</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">API Durumu</span>
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      Sağlıklı
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Veritabanı</span>
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      Sağlıklı
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Redis</span>
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      Sağlıklı
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Agent Sistemi</span>
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                      Aktif
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Sistem Metrikleri</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Toplam İstek:</span>
                    <span className="text-sm font-medium">1,234</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Başarılı İstek:</span>
                    <span className="text-sm font-medium text-green-600">1,198 (97.1%)</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Hatalı İstek:</span>
                    <span className="text-sm font-medium text-red-600">36 (2.9%)</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Ortalama Yanıt Süresi:</span>
                    <span className="text-sm font-medium">145ms</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Aktif Workflow:</span>
                    <span className="text-sm font-medium">{stats?.active_workflows || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}