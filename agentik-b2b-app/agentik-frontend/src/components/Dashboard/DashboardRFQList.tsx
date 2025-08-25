import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { 
  Calendar, 
  ArrowRight, 
  Search, 
  Filter,
  Plus,
  FileText,
  Building,
  Clock,
  Target
} from 'lucide-react'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

interface RFQ {
  id: string
  title: string
  company: string
  status: 'draft' | 'published' | 'closed' | 'awarded'
  deadline: string
  offerCount: number
  createdAt: string
  budget?: number
  category?: string
}

interface DashboardRFQListProps {
  rfqs: RFQ[]
  isLoading?: boolean
}

const statusLabels = {
  draft: { label: 'Taslak', variant: 'outline' as const, color: 'text-gray-600' },
  published: { label: 'Yayında', variant: 'default' as const, color: 'text-blue-600' },
  closed: { label: 'Kapalı', variant: 'secondary' as const, color: 'text-gray-500' },
  awarded: { label: 'İhale Edildi', variant: 'destructive' as const, color: 'text-green-600' }
}

const statusOrder = { draft: 1, published: 2, closed: 3, awarded: 4 }

export default function DashboardRFQList({ rfqs, isLoading }: DashboardRFQListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'date' | 'deadline' | 'offers' | 'status'>('date')
  const [showFilters, setShowFilters] = useState(false)

  const filteredAndSortedRFQs = useMemo(() => {
    let filtered = rfqs

    // Arama filtresi
    if (searchQuery) {
      filtered = filtered.filter(rfq => 
        rfq.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rfq.company.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Durum filtresi
    if (statusFilter !== 'all') {
      filtered = filtered.filter(rfq => rfq.status === statusFilter)
    }

    // Sıralama
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        case 'deadline':
          return new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
        case 'offers':
          return b.offerCount - a.offerCount
        case 'status':
          return statusOrder[a.status] - statusOrder[b.status]
        default:
          return 0
      }
    })

    return filtered
  }, [rfqs, searchQuery, statusFilter, sortBy])

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>RFQ'larım</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500">Yükleniyor...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            RFQ'larım ({rfqs.length})
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="gap-2"
            >
              <Filter className="h-4 w-4" />
              Filtreler
            </Button>
            <Button size="sm" asChild>
              <Link to="/app/rfqs/create" className="gap-2">
                <Plus className="h-4 w-4" />
                Yeni RFQ
              </Link>
            </Button>
          </div>
        </div>

        {/* Arama ve Filtreler */}
        <div className="space-y-4">
          {/* Arama Çubuğu */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="RFQ başlığı veya şirket adı ara..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Gelişmiş Filtreler */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Durum
                </label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Tüm durumlar" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tüm durumlar</SelectItem>
                    <SelectItem value="draft">Taslak</SelectItem>
                    <SelectItem value="published">Yayında</SelectItem>
                    <SelectItem value="closed">Kapalı</SelectItem>
                    <SelectItem value="awarded">İhale Edildi</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Sıralama
                </label>
                <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="date">Oluşturulma Tarihi</SelectItem>
                    <SelectItem value="deadline">Son Tarih</SelectItem>
                    <SelectItem value="offers">Teklif Sayısı</SelectItem>
                    <SelectItem value="status">Durum</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Temizle */}
              <div className="flex items-end">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSearchQuery('')
                    setStatusFilter('all')
                    setSortBy('date')
                  }}
                  className="w-full"
                >
                  Filtreleri Temizle
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {filteredAndSortedRFQs.length === 0 ? (
          <div className="text-center py-12">
            {rfqs.length === 0 ? (
              <div className="text-gray-500">
                <FileText className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                <p className="text-lg font-medium mb-2">Henüz RFQ oluşturmadınız</p>
                <p className="text-sm mb-4">İlk RFQ'nizi oluşturarak tedarikçilerden teklif almaya başlayın</p>
                <Button asChild>
                  <Link to="/app/rfqs/create">İlk RFQ'nizi Oluşturun</Link>
                </Button>
              </div>
            ) : (
              <div className="text-gray-500">
                <p className="text-lg font-medium mb-2">Arama kriterlerine uygun RFQ bulunamadı</p>
                <p className="text-sm">Farklı arama terimleri veya filtreleri deneyin</p>
              </div>
            )}
          </div>
        ) : (
          <>
            {filteredAndSortedRFQs.map((rfq) => (
              <div 
                key={rfq.id} 
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* RFQ Başlığı ve Durum */}
                    <div className="flex items-center gap-3 mb-3">
                      <Link 
                        to={`/app/rfqs/${rfq.id}`} 
                        className="text-lg font-semibold hover:text-blue-600 transition-colors"
                      >
                        {rfq.title}
                      </Link>
                      <Badge variant={statusLabels[rfq.status].variant}>
                        {statusLabels[rfq.status].label}
                      </Badge>
                    </div>

                    {/* RFQ Detayları */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <Building className="h-4 w-4 text-gray-400" />
                        <span className="font-medium">{rfq.company}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span>
                          Son: {format(new Date(rfq.deadline), 'dd MMM yyyy', { locale: tr })}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Target className="h-4 w-4 text-gray-400" />
                        <span>{rfq.offerCount} teklif alındı</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-gray-400" />
                        <span>
                          {format(new Date(rfq.createdAt), 'dd MMM yyyy', { locale: tr })}
                        </span>
                      </div>
                    </div>

                    {/* Kategoriler ve Bütçe */}
                    {(rfq.category || rfq.budget) && (
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                        {rfq.category && (
                          <Badge variant="outline" className="text-xs">
                            {rfq.category}
                          </Badge>
                        )}
                        {rfq.budget && (
                          <span className="font-medium">
                            Bütçe: {rfq.budget.toLocaleString('tr-TR')} TL
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Aksiyon Butonları */}
                  <div className="flex items-center gap-2 ml-4">
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/app/rfqs/${rfq.id}`}>
                        Detay
                      </Link>
                    </Button>
                    {rfq.offerCount > 0 && (
                      <Button variant="default" size="sm" asChild>
                        <Link to={`/app/rfqs/${rfq.id}/offers`}>
                          Teklifleri Gör
                        </Link>
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Tümünü Gör */}
            <div className="pt-4 border-t">
              <Button variant="ghost" className="w-full" asChild>
                <Link to="/app/rfqs" className="flex items-center justify-center gap-2">
                  Tüm RFQ'ları Görüntüle
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
