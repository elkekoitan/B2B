import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Search, 
  Filter, 
  Plus, 
  Calendar, 
  Building, 
  Eye,
  Edit,
  Trash2
} from 'lucide-react'

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
import { apiClient } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const statusLabels = {
  draft: { label: 'Taslak', variant: 'outline' as const },
  published: { label: 'Yayında', variant: 'info' as const },
  closed: { label: 'Kapalı', variant: 'secondary' as const },
  awarded: { label: 'İhale Edildi', variant: 'success' as const }
}

interface RFQ {
  id: string
  title: string
  company: string
  category: string
  status: 'draft' | 'published' | 'closed' | 'awarded'
  deadline: string
  offerCount: number
  createdAt: string
  budget?: number
}

export default function RFQListPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  // Fetch RFQs
  const { data: rfqs, isLoading, error } = useQuery({
    queryKey: ['rfqs', user?.id, searchTerm, statusFilter, categoryFilter],
    queryFn: async () => {
      // Mock data for now - replace with actual API call
      const mockRFQs: RFQ[] = [
        {
          id: '1',
          title: 'Büro Mobilyası Tedariki',
          company: 'ABC Şirketi',
          category: 'Mobilya',
          status: 'published',
          deadline: '2025-01-15T00:00:00Z',
          offerCount: 5,
          createdAt: '2025-01-01T10:00:00Z',
          budget: 50000
        },
        {
          id: '2',
          title: 'IT Ekipmanları',
          company: 'XYZ Ltd',
          category: 'Teknoloji',
          status: 'draft',
          deadline: '2025-01-20T00:00:00Z',
          offerCount: 0,
          createdAt: '2025-01-02T14:30:00Z'
        },
        {
          id: '3',
          title: 'Temizlik Malzemeleri',
          company: 'Temiz A.Ş.',
          category: 'Temizlik',
          status: 'closed',
          deadline: '2024-12-30T00:00:00Z',
          offerCount: 8,
          createdAt: '2024-12-15T09:00:00Z',
          budget: 25000
        },
        {
          id: '4',
          title: 'Kırtasiye Malzemeleri',
          company: 'Okul Ltd',
          category: 'Kırtasiye',
          status: 'awarded',
          deadline: '2024-12-25T00:00:00Z',
          offerCount: 12,
          createdAt: '2024-12-10T16:45:00Z',
          budget: 15000
        }
      ]
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Apply filters
      let filteredRFQs = mockRFQs
      
      if (searchTerm) {
        filteredRFQs = filteredRFQs.filter(rfq =>
          rfq.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          rfq.company.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      if (statusFilter !== 'all') {
        filteredRFQs = filteredRFQs.filter(rfq => rfq.status === statusFilter)
      }
      
      if (categoryFilter !== 'all') {
        filteredRFQs = filteredRFQs.filter(rfq => rfq.category === categoryFilter)
      }
      
      return filteredRFQs
    },
    enabled: !!user
  })

  const categories = ['all', 'Mobilya', 'Teknoloji', 'Temizlik', 'Kırtasiye']
  const statuses = [
    { value: 'all', label: 'Tümü' },
    { value: 'draft', label: 'Taslak' },
    { value: 'published', label: 'Yayında' },
    { value: 'closed', label: 'Kapalı' },
    { value: 'awarded', label: 'İhale Edildi' }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">RFQ'lar yüklenirken hata oluştu.</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          Tekrar Dene
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">RFQ'larım</h1>
          <p className="text-gray-600 mt-1">
            Oluşturduğunuz RFQ'ları görüntüleyin ve yönetin.
          </p>
        </div>
        <Button asChild>
          <Link to="/app/rfqs/create" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Yeni RFQ Oluştur
          </Link>
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="RFQ ara..."
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

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="all">Tüm Kategoriler</option>
              {categories.filter(cat => cat !== 'all').map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>

            {/* Clear Filters */}
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('all')
                setCategoryFilter('all')
              }}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Filtreleri Temizle
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* RFQ Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam RFQ</p>
                <p className="text-2xl font-bold">{rfqs?.length || 0}</p>
              </div>
              <div className="p-2 bg-blue-100 rounded-full">
                <Building className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Yayında</p>
                <p className="text-2xl font-bold text-green-600">
                  {rfqs?.filter(rfq => rfq.status === 'published').length || 0}
                </p>
              </div>
              <div className="p-2 bg-green-100 rounded-full">
                <Eye className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Taslak</p>
                <p className="text-2xl font-bold text-orange-600">
                  {rfqs?.filter(rfq => rfq.status === 'draft').length || 0}
                </p>
              </div>
              <div className="p-2 bg-orange-100 rounded-full">
                <Edit className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Tamamlanan</p>
                <p className="text-2xl font-bold text-purple-600">
                  {rfqs?.filter(rfq => rfq.status === 'awarded').length || 0}
                </p>
              </div>
              <div className="p-2 bg-purple-100 rounded-full">
                <Calendar className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* RFQ Table */}
      <Card>
        <CardHeader>
          <CardTitle>RFQ Listesi</CardTitle>
        </CardHeader>
        <CardContent>
          {!rfqs || rfqs.length === 0 ? (
            <div className="text-center py-12">
              <Building className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p className="text-gray-500 mb-4">
                {searchTerm || statusFilter !== 'all' || categoryFilter !== 'all' 
                  ? 'Filtrelere uygun RFQ bulunamadı.' 
                  : 'Henüz RFQ oluşturmadınız.'
                }
              </p>
              <Button asChild>
                <Link to="/app/rfqs/create">İlk RFQ'nizi Oluşturun</Link>
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Başlık</TableHead>
                  <TableHead>Şirket</TableHead>
                  <TableHead>Kategori</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Son Tarih</TableHead>
                  <TableHead>Teklifler</TableHead>
                  <TableHead>Bütçe</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rfqs.map((rfq) => (
                  <TableRow key={rfq.id}>
                    <TableCell className="font-medium">
                      <Link 
                        to={`/app/rfqs/${rfq.id}`}
                        className="hover:text-blue-600 transition-colors"
                      >
                        {rfq.title}
                      </Link>
                    </TableCell>
                    <TableCell>{rfq.company}</TableCell>
                    <TableCell>{rfq.category}</TableCell>
                    <TableCell>
                      <Badge variant={statusLabels[rfq.status].variant}>
                        {statusLabels[rfq.status].label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        {format(new Date(rfq.deadline), 'dd MMM yyyy', { locale: tr })}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className={rfq.offerCount > 0 ? 'text-green-600 font-medium' : 'text-gray-500'}>
                        {rfq.offerCount}
                      </span>
                    </TableCell>
                    <TableCell>
                      {rfq.budget ? `₺${rfq.budget.toLocaleString()}` : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/app/rfqs/${rfq.id}`}>
                            <Eye className="h-4 w-4" />
                          </Link>
                        </Button>
                        {rfq.status === 'draft' && (
                          <Button variant="outline" size="sm" asChild>
                            <Link to={`/app/rfqs/${rfq.id}/edit`}>
                              <Edit className="h-4 w-4" />
                            </Link>
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
