import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useApiClient } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import {
  FileText,
  Plus,
  Search,
  Filter,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  DollarSign,
  Calendar,
  ChevronRight,
  Loader2,
  RefreshCw
} from 'lucide-react'
import type { RFQ, Offer } from '../lib/supabase'

interface DashboardStats {
  total_rfqs: number
  active_rfqs: number
  completed_rfqs: number
  avg_response_time?: number
  avg_offers_per_rfq?: number
  top_categories: { category: string; count: number }[]
}

const statusColors = {
  draft: 'bg-gray-100 text-gray-800',
  published: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const urgencyColors = {
  low: 'text-green-600',
  medium: 'text-yellow-600',
  high: 'text-red-600',
}

export function DashboardPage() {
  const { userProfile } = useAuth()
  const apiClient = useApiClient()
  const navigate = useNavigate()
  const [rfqs, setRfqs] = useState<RFQ[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('')
  const [page, setPage] = useState(1)

  const loadDashboardData = async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true)
      else setLoading(true)

      // Load RFQs from backend API
      const rfqsResponse = await apiClient.getRFQs({
        page,
        per_page: 10,
        status: filterStatus || undefined,
      })

      // Load analytics from backend API
      const analyticsResponse = await apiClient.getRFQAnalytics()

      if (rfqsResponse.success && rfqsResponse.data) {
        setRfqs(rfqsResponse.data)
        console.log('✅ RFQs loaded from backend:', rfqsResponse.data.length, 'items')
      } else {
        console.warn('⚠️ Failed to load RFQs:', rfqsResponse)
        setRfqs([])
      }

      if (analyticsResponse.success && analyticsResponse.data) {
        setStats(analyticsResponse.data as DashboardStats)
        console.log('✅ Analytics loaded from backend:', analyticsResponse.data)
      } else {
        console.warn('⚠️ Failed to load analytics:', analyticsResponse)
        // Set default stats if analytics fail
        setStats({
          total_rfqs: rfqsResponse.data?.length || 0,
          active_rfqs: rfqsResponse.data?.filter((rfq: any) => rfq.status === 'published').length || 0,
          completed_rfqs: rfqsResponse.data?.filter((rfq: any) => rfq.status === 'completed').length || 0,
          avg_offers_per_rfq: 0,
          top_categories: []
        })
      }
    } catch (error) {
      console.error('❌ Dashboard data loading failed:', error)
      // Set empty data on error
      setRfqs([])
      setStats({
        total_rfqs: 0,
        active_rfqs: 0,
        completed_rfqs: 0,
        avg_offers_per_rfq: 0,
        top_categories: []
      })
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
  }, [page, filterStatus])

  const filteredRfqs = rfqs.filter(rfq =>
    rfq.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rfq.category.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const getStatusBadge = (status: string) => {
    const colorClass = statusColors[status as keyof typeof statusColors] || statusColors.draft
    const statusText = {
      draft: 'Taslak',
      published: 'Yayınlandı',
      in_progress: 'İşlemde',
      completed: 'Tamamlandı',
      cancelled: 'İptal Edildi'
    }[status] || status

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {statusText}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-indigo-600" />
          <p className="text-gray-600">Veriler yükleniyor...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Hoş geldiniz, {userProfile?.full_name || userProfile?.email}
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => loadDashboardData(true)}
                disabled={refreshing}
                className="flex items-center gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                Yenile
              </Button>
              <Button
                onClick={() => navigate('/rfq/new')}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Yeni RFQ
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Clock className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Aktif RFQ</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.active_rfqs}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Tamamlanan</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.completed_rfqs}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Ort. Teklif/RFQ</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.avg_offers_per_rfq?.toFixed(1) || '0'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* RFQ List */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>RFQ Listesi</CardTitle>
                <CardDescription>
                  Oluşturduğunuz teklif taleplerini görüntüleyin ve yönetin
                </CardDescription>
              </div>
            </div>
            
            {/* Search and Filter */}
            <div className="flex flex-col sm:flex-row gap-4 mt-4">
              <div className="relative flex-1">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="RFQ ara..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md bg-white text-sm"
                >
                  <option value="">Tüm Durumlar</option>
                  <option value="draft">Taslak</option>
                  <option value="published">Yayınlandı</option>
                  <option value="in_progress">İşlemde</option>
                  <option value="completed">Tamamlandı</option>
                </select>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            {filteredRfqs.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {searchTerm || filterStatus ? 'Sonuç bulunamadı' : 'Henüz RFQ yok'}
                </h3>
                <p className="text-gray-600 mb-6">
                  {searchTerm || filterStatus 
                    ? 'Arama kriterlerinizle eşleşen RFQ bulunamadı.'
                    : 'İlk RFQ\'nizi oluşturmak için başlayın.'}
                </p>
                {!searchTerm && !filterStatus && (
                  <Button onClick={() => navigate('/rfq/new')}>
                    İlk RFQ\'nizi Oluşturun
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredRfqs.map((rfq) => (
                  <div
                    key={rfq.id}
                    className="border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/rfq/${rfq.id}`)}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {rfq.title}
                        </h3>
                        <p className="text-gray-600 text-sm line-clamp-2">
                          {rfq.description}
                        </p>
                      </div>
                      <div className="ml-4 text-right">
                        {getStatusBadge(rfq.status)}
                        {rfq.urgency && (
                          <p className={`text-xs mt-1 font-medium ${
                            urgencyColors[rfq.urgency as keyof typeof urgencyColors]
                          }`}>
                            {rfq.urgency === 'high' ? 'Acil' : 
                             rfq.urgency === 'medium' ? 'Orta' : 'Düşük'} Öncelik
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Kategori:</span>
                        <p className="capitalize">{rfq.category}</p>
                      </div>
                      <div>
                        <span className="font-medium">Miktar:</span>
                        <p>{rfq.quantity} {rfq.unit}</p>
                      </div>
                      <div>
                        <span className="font-medium">Son Tarih:</span>
                        <p>{formatDate(rfq.deadline)}</p>
                      </div>
                      <div>
                        <span className="font-medium">Oluşturma:</span>
                        <p>{formatDate(rfq.created_at)}</p>
                      </div>
                    </div>
                    
                    {(rfq.budget_min || rfq.budget_max) && (
                      <div className="mt-4 pt-4 border-t">
                        <span className="text-sm font-medium text-gray-600">Bütçe: </span>
                        <span className="text-sm text-gray-900">
                          {rfq.budget_min && rfq.budget_max
                            ? `${formatCurrency(rfq.budget_min)} - ${formatCurrency(rfq.budget_max)}`
                            : rfq.budget_min
                            ? `Min: ${formatCurrency(rfq.budget_min)}`
                            : `Max: ${formatCurrency(rfq.budget_max!)}`
                          }
                        </span>
                      </div>
                    )}
                    
                    <div className="flex justify-end mt-4">
                      <ChevronRight className="h-5 w-5 text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}