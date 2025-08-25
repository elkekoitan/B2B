import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Package, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  ArrowRight,
  Search,
  Filter,
  Calendar,
  Building,
  DollarSign,
  MessageSquare
} from 'lucide-react'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useAuth } from '@/contexts/AuthContext'
import { apiClient } from '@/lib/api'

const statusLabels = {
  pending: { label: 'Bekliyor', variant: 'warning' as const },
  accepted: { label: 'Kabul Edildi', variant: 'success' as const },
  rejected: { label: 'Reddedildi', variant: 'destructive' as const },
  expired: { label: 'Süresi Dolmuş', variant: 'secondary' as const },
  withdrawn: { label: 'Çekildi', variant: 'outline' as const }
}

interface Offer {
  id: string
  rfqId: string
  rfqTitle: string
  companyName: string
  totalPrice: number
  unitPrice: number
  currency: string
  quantity: number
  deliveryTime: number
  validUntil: string
  status: 'pending' | 'accepted' | 'rejected' | 'expired' | 'withdrawn'
  submittedAt: string
  lastUpdated: string
  description: string
  specifications: string
  attachments: Array<{
    id: string
    name: string
    url: string
  }>
  notes?: string
}

export default function OffersPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [dateFilter, setDateFilter] = useState<string>('all')

  // Fetch offers
  const { data: offers, isLoading } = useQuery({
    queryKey: ['offers', user?.id, searchTerm, statusFilter, dateFilter],
    queryFn: async () => {
      // Mock data for now - replace with actual API call
      const mockOffers: Offer[] = [
        {
          id: '1',
          rfqId: 'rfq-1',
          rfqTitle: 'Büro Mobilyası Tedariki',
          companyName: 'ABC Şirketi',
          totalPrice: 135000,
          unitPrice: 771.43,
          currency: 'TRY',
          quantity: 175,
          deliveryTime: 14,
          validUntil: '2025-02-01T00:00:00Z',
          status: 'pending',
          submittedAt: '2025-01-03T09:15:00Z',
          lastUpdated: '2025-01-05T14:30:00Z',
          description: 'Premium kalite büro mobilyaları. 5 yıl garanti, ücretsiz montaj ve 2 yıl bakım hizmeti dahil.',
          specifications: 'Tüm ürünler ergonomik tasarım standartlarına uygun, FSC sertifikalı malzemeler kullanılmıştır.',
          attachments: [
            {
              id: '1',
              name: 'Teklif_Detayi.pdf',
              url: '#'
            },
            {
              id: '2',
              name: 'Urun_Katalog.pdf',
              url: '#'
            }
          ],
          notes: 'Montaj hizmet ekibi dahil, proje yöneticisi atanacaktır.'
        },
        {
          id: '2',
          rfqId: 'rfq-2',
          rfqTitle: 'IT Ekipmanları',
          companyName: 'XYZ Ltd',
          totalPrice: 89500,
          unitPrice: 1790,
          currency: 'TRY',
          quantity: 50,
          deliveryTime: 7,
          validUntil: '2025-01-28T00:00:00Z',
          status: 'accepted',
          submittedAt: '2025-01-02T14:20:00Z',
          lastUpdated: '2025-01-08T11:15:00Z',
          description: 'Son teknoloji IT ekipmanları, 3 yıl garanti ve teknik destek dahil.',
          specifications: 'Tüm cihazlar işletmeli ve yazılım kurulumu yapılmış olarak teslim edilecektir.',
          attachments: [
            {
              id: '3',
              name: 'Teknik_Ozellikler.pdf',
              url: '#'
            }
          ]
        },
        {
          id: '3',
          rfqId: 'rfq-3',
          rfqTitle: 'Temizlik Malzemeleri',
          companyName: 'Temiz A.Ş.',
          totalPrice: 25750,
          unitPrice: 515,
          currency: 'TRY',
          quantity: 50,
          deliveryTime: 21,
          validUntil: '2024-12-28T00:00:00Z',
          status: 'expired',
          submittedAt: '2024-12-20T16:45:00Z',
          lastUpdated: '2024-12-28T23:59:59Z',
          description: 'Profesyonel temizlik malzemeleri, çevre dostu formul.',
          specifications: 'Tüm ürünler SA 8000 ve ISO 14001 sertifikalıdır.',
          attachments: []
        },
        {
          id: '4',
          rfqId: 'rfq-4',
          rfqTitle: 'Kırtasiye Malzemeleri',
          companyName: 'Okul Ltd',
          totalPrice: 12800,
          unitPrice: 64,
          currency: 'TRY',
          quantity: 200,
          deliveryTime: 10,
          validUntil: '2024-12-22T00:00:00Z',
          status: 'rejected',
          submittedAt: '2024-12-18T10:30:00Z',
          lastUpdated: '2024-12-20T09:45:00Z',
          description: 'Kaliteli kırtasiye malzemeleri, toplu sipariş indirimi.',
          specifications: 'Orijinal markalı ürünler, fatura ile teslim.',
          attachments: [],
          notes: 'Müşteri daha ekonomik alternatif tercih etti.'
        }
      ]
      
      // Apply filters
      let filteredOffers = mockOffers
      
      if (searchTerm) {
        filteredOffers = filteredOffers.filter(offer =>
          offer.rfqTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
          offer.companyName.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      if (statusFilter !== 'all') {
        filteredOffers = filteredOffers.filter(offer => offer.status === statusFilter)
      }
      
      if (dateFilter !== 'all') {
        const now = new Date()
        const daysAgo = {
          '7': 7,
          '30': 30,
          '90': 90
        }[dateFilter]
        
        if (daysAgo) {
          const cutoffDate = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000)
          filteredOffers = filteredOffers.filter(offer =>
            new Date(offer.submittedAt) >= cutoffDate
          )
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 500))
      return filteredOffers
    },
    enabled: !!user
  })

  const statuses = [
    { value: 'all', label: 'Tümü' },
    { value: 'pending', label: 'Bekliyor' },
    { value: 'accepted', label: 'Kabul Edildi' },
    { value: 'rejected', label: 'Reddedildi' },
    { value: 'expired', label: 'Süresi Dolmuş' }
  ]

  const dateRanges = [
    { value: 'all', label: 'Tüm Zamanlar' },
    { value: '7', label: 'Son 7 Gün' },
    { value: '30', label: 'Son 30 Gün' },
    { value: '90', label: 'Son 90 Gün' }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Calculate stats
  const totalOffers = offers?.length || 0
  const pendingOffers = offers?.filter(o => o.status === 'pending').length || 0
  const acceptedOffers = offers?.filter(o => o.status === 'accepted').length || 0
  const totalValue = offers?.filter(o => o.status === 'accepted').reduce((sum, o) => sum + o.totalPrice, 0) || 0

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tekliflerim</h1>
          <p className="text-gray-600 mt-1">
            Gönderdiğiniz teklifleri takip edin ve yönetin.
          </p>
        </div>
        
        <Button asChild>
          <Link to="/app/suppliers" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Yeni Teklif Oluştur
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam Teklif</p>
                <p className="text-2xl font-bold">{totalOffers}</p>
              </div>
              <Package className="h-6 w-6 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bekleyen</p>
                <p className="text-2xl font-bold text-orange-600">{pendingOffers}</p>
              </div>
              <Clock className="h-6 w-6 text-orange-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Kabul Edildi</p>
                <p className="text-2xl font-bold text-green-600">{acceptedOffers}</p>
              </div>
              <CheckCircle className="h-6 w-6 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam Değer</p>
                <p className="text-2xl font-bold text-blue-600">
                  ₺{totalValue.toLocaleString()}
                </p>
              </div>
              <DollarSign className="h-6 w-6 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Teklif ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {statuses.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>

            {/* Date Filter */}
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {dateRanges.map((range) => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>

            {/* Clear Filters */}
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('all')
                setDateFilter('all')
              }}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Filtreleri Temizle
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Offers Table */}
      <Card>
        <CardHeader>
          <CardTitle>Teklifler ({offers?.length || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {!offers || offers.length === 0 ? (
            <div className="text-center py-12">
              <Package className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p className="text-gray-500 mb-4">
                {searchTerm || statusFilter !== 'all' || dateFilter !== 'all'
                  ? 'Arama kriterlerinize uygun teklif bulunamadı.'
                  : 'Henüz teklif göndermediniz.'
                }
              </p>
              <Button asChild>
                <Link to="/app/suppliers">
                  İlk Teklifinizi Gönderin
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {offers.map((offer) => (
                <div 
                  key={offer.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <Link 
                          to={`/app/rfqs/${offer.rfqId}`}
                          className="font-semibold text-lg hover:text-blue-600 transition-colors"
                        >
                          {offer.rfqTitle}
                        </Link>
                        <Badge variant={statusLabels[offer.status].variant}>
                          {statusLabels[offer.status].label}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                        <Building className="h-4 w-4" />
                        <span>{offer.companyName}</span>
                      </div>
                      
                      <p className="text-gray-700 text-sm mb-2">{offer.description}</p>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-2xl font-bold text-green-600">
                        ₺{offer.totalPrice.toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-500">
                        ₺{offer.unitPrice.toFixed(2)}/birim
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <span className="text-xs text-gray-500">Miktar</span>
                      <p className="font-medium">{offer.quantity.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Teslimat</span>
                      <p className="font-medium">{offer.deliveryTime} gün</p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Geçerlilik</span>
                      <p className="font-medium">
                        {format(new Date(offer.validUntil), 'dd MMM yyyy', { locale: tr })}
                      </p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-500">Gönderilme</span>
                      <p className="font-medium">
                        {format(new Date(offer.submittedAt), 'dd MMM yyyy', { locale: tr })}
                      </p>
                    </div>
                  </div>

                  {offer.notes && (
                    <div className="mb-3">
                      <span className="text-xs text-gray-500">Notlar:</span>
                      <p className="text-sm text-gray-700">{offer.notes}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-3 border-t">
                    <div className="flex items-center gap-2">
                      {offer.attachments.length > 0 && (
                        <span className="text-sm text-gray-500">
                          {offer.attachments.length} ek dosya
                        </span>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <MessageSquare className="h-4 w-4 mr-1" />
                        Mesaj
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/app/rfqs/${offer.rfqId}`}>
                          RFQ Detayı
                        </Link>
                      </Button>
                      {offer.status === 'pending' && (
                        <Button size="sm">
                          Güncelle
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
