import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useApiClient } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '../components/ui/Card'
import { LoadingSpinner } from '../components/LoadingSpinner'
import {
  ArrowLeft,
  Calendar,
  MapPin,
  Package,
  DollarSign,
  Clock,
  Users,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  Download,
  RefreshCw,
  Play
} from 'lucide-react'
import type { RFQ, Offer } from '../lib/supabase'

interface RFQDetailData {
  rfq: RFQ
  offers: Offer[]
  offers_count: number
  analysis?: {
    total_offers: number
    price_range: { min: number; max: number; avg: number }
    delivery_time_range: { min: number; max: number; avg: number }
    best_price_offer_id?: string
    fastest_delivery_offer_id?: string
  }
}

interface JobStatus {
  job_id: string
  status: string
  created_at: string
  updated_at?: string
  result?: any
  error?: string
}

const statusColors = {
  draft: 'bg-gray-100 text-gray-800',
  published: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const offerStatusColors = {
  pending: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export function RFQDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const apiClient = useApiClient()
  const [data, setData] = useState<RFQDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [startingWorkflow, setStartingWorkflow] = useState(false)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState('')

  const loadRFQDetails = async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true)
      else setLoading(true)
      setError('')

      const response = await apiClient.getRFQ(id!)
      
      if (response.success) {
        setData(response.data)
      } else {
        setError('RFQ detayları yüklenirken hata oluştu')
      }
    } catch (err: any) {
      setError(err.message || 'RFQ detayları yüklenirken hata oluştu')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const startWorkflow = async () => {
    if (!data?.rfq) return

    setStartingWorkflow(true)
    try {
      const response = await apiClient.startWorkflow({
        job_type: 'rfq_process',
        rfq_id: data.rfq.id,
        payload: { rfq: data.rfq }
      })

      if (response.success && response.data?.job_id) {
        const jobId = response.data.job_id
        // Start polling job status
        pollJobStatus(jobId)
      } else {
        setError('Workflow başlatma hatası')
      }
    } catch (err: any) {
      setError(err.message || 'Workflow başlatma hatası')
    } finally {
      setStartingWorkflow(false)
    }
  }

  const pollJobStatus = (jobId: string) => {
    const poll = async () => {
      try {
        const response = await apiClient.getJobStatus(jobId)
        if (response.success) {
          setJobStatus(response.data)
          
          if (response.data.status === 'completed') {
            // Reload RFQ data to show updated offers
            loadRFQDetails(true)
          } else if (response.data.status !== 'failed') {
            // Continue polling
            setTimeout(poll, 5000)
          }
        }
      } catch (error) {
        console.error('Job status polling error:', error)
      }
    }
    poll()
  }

  useEffect(() => {
    if (id) {
      loadRFQDetails()
    }
  }, [id])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('tr-TR')
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const getStatusBadge = (status: string, isOffer = false) => {
    const colors = isOffer ? offerStatusColors : statusColors
    const colorClass = colors[status as keyof typeof colors] || colors.pending
    
    const statusTexts = isOffer ? {
      pending: 'Beklemede',
      submitted: 'Gönderildi',
      accepted: 'Kabul Edildi',
      rejected: 'Reddedildi'
    } : {
      draft: 'Taslak',
      published: 'Yayınlandı',
      in_progress: 'İşlemde',
      completed: 'Tamamlandı',
      cancelled: 'İptal Edildi'
    }
    
    const statusText = statusTexts[status as keyof typeof statusTexts] || status

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {statusText}
      </span>
    )
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full">
          <CardContent className="text-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Hata Oluştu
            </h2>
            <p className="text-gray-600 mb-4">{error || 'RFQ bulunamadı'}</p>
            <Button onClick={() => navigate('/dashboard')}>
              Dashboard'a Dön
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const { rfq, offers, analysis } = data

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Geri
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{rfq.title}</h1>
              <p className="text-gray-600">RFQ ID: {rfq.id.slice(-8)}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {getStatusBadge(rfq.status)}
            <Button
              variant="outline"
              onClick={() => loadRFQDetails(true)}
              disabled={refreshing}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Yenile
            </Button>
            
            {rfq.status === 'published' && (
              <Button
                onClick={startWorkflow}
                disabled={startingWorkflow}
                className="flex items-center gap-2"
              >
                <Play className="h-4 w-4" />
                {startingWorkflow ? 'Başlatılıyor...' : 'Workflow Başlat'}
              </Button>
            )}
          </div>
        </div>

        {/* Job Status */}
        {jobStatus && (
          <Card className="mb-6">
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    jobStatus.status === 'completed' ? 'bg-green-500' :
                    jobStatus.status === 'failed' ? 'bg-red-500' :
                    jobStatus.status === 'in_progress' ? 'bg-yellow-500 animate-pulse' :
                    'bg-gray-500'
                  }`} />
                  <span className="text-sm font-medium">
                    Workflow Durumu: {jobStatus.status === 'completed' ? 'Tamamlandı' :
                    jobStatus.status === 'failed' ? 'Hata' :
                    jobStatus.status === 'in_progress' ? 'İşlemde' : 'Beklemede'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {jobStatus.job_id}
                  </span>
                </div>
                {jobStatus.error && (
                  <span className="text-xs text-red-600">{jobStatus.error}</span>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* RFQ Details */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>RFQ Detayları</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Açıklama</h3>
                    <p className="text-gray-600 leading-relaxed">{rfq.description}</p>
                  </div>
                  
                  {rfq.requirements && (
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Özel Gereksinimler</h3>
                      <p className="text-gray-600 leading-relaxed">{rfq.requirements}</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div className="flex items-center gap-3">
                      <Package className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-600">Miktar</p>
                        <p className="font-medium">{rfq.quantity} {rfq.unit}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Calendar className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-600">Son Tarih</p>
                        <p className="font-medium">{formatDate(rfq.deadline)}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <MapPin className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-600">Teslimat</p>
                        <p className="font-medium">{rfq.delivery_location}</p>
                      </div>
                    </div>
                    
                    {(rfq.budget_min || rfq.budget_max) && (
                      <div className="flex items-center gap-3">
                        <DollarSign className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-600">Bütçe</p>
                          <p className="font-medium">
                            {rfq.budget_min && rfq.budget_max
                              ? `${formatCurrency(rfq.budget_min)} - ${formatCurrency(rfq.budget_max)}`
                              : rfq.budget_min
                              ? `Min: ${formatCurrency(rfq.budget_min)}`
                              : `Max: ${formatCurrency(rfq.budget_max!)}`
                            }
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Offers */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Gelen Teklifler ({offers.length})</CardTitle>
                    <CardDescription>
                      Tedarikçilerden gelen teklifler
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {offers.length === 0 ? (
                  <div className="text-center py-8">
                    <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Henüz teklif yok
                    </h3>
                    <p className="text-gray-600">
                      Tedarikçilerden teklif gelmesini bekleyin veya workflow başlatın.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {offers.map((offer) => (
                      <div
                        key={offer.id}
                        className="border rounded-lg p-4 hover:shadow-sm transition-shadow"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <p className="font-medium text-gray-900">
                              Tedarikçi: {offer.supplier_id}
                            </p>
                            <p className="text-sm text-gray-600">
                              Teklif ID: {offer.id.slice(-8)}
                            </p>
                          </div>
                          {getStatusBadge(offer.status, true)}
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Birim Fiyat:</span>
                            <p className="font-medium">{formatCurrency(offer.unit_price)}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">Toplam Fiyat:</span>
                            <p className="font-medium text-lg">{formatCurrency(offer.total_price)}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">Teslimat Süresi:</span>
                            <p className="font-medium">{offer.delivery_time} gün</p>
                          </div>
                          <div>
                            <span className="text-gray-600">Gönderim:</span>
                            <p className="font-medium">{formatDate(offer.submitted_at)}</p>
                          </div>
                        </div>
                        
                        {offer.terms && (
                          <div className="mt-3 pt-3 border-t">
                            <span className="text-sm text-gray-600">Koşullar: </span>
                            <span className="text-sm">{offer.terms}</span>
                          </div>
                        )}
                        
                        {offer.verification_score && (
                          <div className="mt-2">
                            <span className="text-xs text-gray-500">
                              Doğrulama Skoru: {(offer.verification_score * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Analysis Sidebar */}
          <div className="space-y-6">
            {analysis && analysis.total_offers > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Teklif Analizi
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600">Fiyat Aralığı</p>
                      <p className="font-medium">
                        {formatCurrency(analysis.price_range.min)} - {formatCurrency(analysis.price_range.max)}
                      </p>
                      <p className="text-xs text-gray-500">
                        Ortalama: {formatCurrency(analysis.price_range.avg)}
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-600">Teslimat Süresi</p>
                      <p className="font-medium">
                        {analysis.delivery_time_range.min} - {analysis.delivery_time_range.max} gün
                      </p>
                      <p className="text-xs text-gray-500">
                        Ortalama: {analysis.delivery_time_range.avg.toFixed(1)} gün
                      </p>
                    </div>
                    
                    {analysis.best_price_offer_id && (
                      <div className="pt-4 border-t">
                        <p className="text-sm font-medium text-green-600">
                          En iyi fiyat: {analysis.best_price_offer_id.slice(-8)}
                        </p>
                      </div>
                    )}
                    
                    {analysis.fastest_delivery_offer_id && (
                      <div>
                        <p className="text-sm font-medium text-blue-600">
                          En hızlı teslimat: {analysis.fastest_delivery_offer_id.slice(-8)}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
            
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Hızlı Bilgiler</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Kategori:</span>
                    <span className="text-sm font-medium capitalize">{rfq.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Oluşturma:</span>
                    <span className="text-sm font-medium">{formatDate(rfq.created_at)}</span>
                  </div>
                  {rfq.updated_at && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Güncelleme:</span>
                      <span className="text-sm font-medium">{formatDate(rfq.updated_at)}</span>
                    </div>
                  )}
                  {rfq.urgency && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Öncelik:</span>
                      <span className={`text-sm font-medium ${
                        rfq.urgency === 'high' ? 'text-red-600' :
                        rfq.urgency === 'medium' ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {rfq.urgency === 'high' ? 'Yüksek' : 
                         rfq.urgency === 'medium' ? 'Orta' : 'Düşük'}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}