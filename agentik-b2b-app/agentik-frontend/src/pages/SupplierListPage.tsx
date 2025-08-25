import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Search, 
  Filter, 
  Star,
  MapPin,
  Building,
  Package,
  Phone,
  Mail,
  ExternalLink,
  Shield
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface Supplier {
  id: string
  name: string
  description: string
  category: string[]
  location: string
  rating: number
  reviewCount: number
  verified: boolean
  responseTime: string
  completedOrders: number
  logo?: string
  contact: {
    email: string
    phone: string
    website?: string
  }
  specialties: string[]
  certifications: string[]
  joinedDate: string
}

export default function SupplierListPage() {
  const { user } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [locationFilter, setLocationFilter] = useState<string>('all')
  const [verifiedOnly, setVerifiedOnly] = useState(false)
  const [minRating, setMinRating] = useState(0)

  // Fetch suppliers
  const { data: suppliers, isLoading } = useQuery({
    queryKey: ['suppliers', searchTerm, categoryFilter, locationFilter, verifiedOnly, minRating],
    queryFn: async () => {
      // Mock data for now - replace with actual API call
      const mockSuppliers: Supplier[] = [
        {
          id: '1',
          name: 'Mobilya Pro A.Ş.',
          description: 'Premium kalite büro mobilyaları üretimi ve tedariki. 15 yıllık deneyim ile müşteri memnuniyeti odaklı hizmet.',
          category: ['Mobilya', 'Büro Ekipmanları'],
          location: 'İstanbul, Türkiye',
          rating: 4.8,
          reviewCount: 127,
          verified: true,
          responseTime: '2-4 saat',
          completedOrders: 235,
          contact: {
            email: 'info@mobilyapro.com',
            phone: '+90 212 555 0101',
            website: 'https://mobilyapro.com'
          },
          specialties: ['Ergonomik Mobilya', 'Özel Tasarım', 'Toplu Projeler'],
          certifications: ['ISO 9001', 'TSE'],
          joinedDate: '2020-03-15'
        },
        {
          id: '2',
          name: 'Ofis Dünyası Ltd.',
          description: 'Kapsamlı ofis çözümleri ve ekipmanları. Modern tasarım anlayışı ile profesyonel hizmet.',
          category: ['Mobilya', 'Teknoloji', 'Kırtasiye'],
          location: 'Ankara, Türkiye',
          rating: 4.5,
          reviewCount: 89,
          verified: true,
          responseTime: '1-2 saat',
          completedOrders: 158,
          contact: {
            email: 'iletisim@ofisdunyasi.com',
            phone: '+90 312 555 0202'
          },
          specialties: ['Ofis Planlaması', 'Teknoloji Entegrasyonu'],
          certifications: ['CE', 'ISO 14001'],
          joinedDate: '2019-08-22'
        },
        {
          id: '3',
          name: 'Metro Mobilya',
          description: 'Ekonomik çözümler ve hızlı teslimat. Geniş ürün yelpazesi ile her bütçeye uygun seçenekler.',
          category: ['Mobilya'],
          location: 'İzmir, Türkiye',
          rating: 4.2,
          reviewCount: 203,
          verified: false,
          responseTime: '4-6 saat',
          completedOrders: 312,
          contact: {
            email: 'satış@metromobilya.com',
            phone: '+90 232 555 0303',
            website: 'https://metromobilya.com'
          },
          specialties: ['Ekonomik Çözümler', 'Hızlı Teslimat'],
          certifications: ['TSE'],
          joinedDate: '2021-01-10'
        }
      ]
      
      // Apply filters
      let filteredSuppliers = mockSuppliers
      
      if (searchTerm) {
        filteredSuppliers = filteredSuppliers.filter(supplier =>
          supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          supplier.description.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      if (categoryFilter !== 'all') {
        filteredSuppliers = filteredSuppliers.filter(supplier =>
          supplier.category.includes(categoryFilter)
        )
      }
      
      if (locationFilter !== 'all') {
        filteredSuppliers = filteredSuppliers.filter(supplier =>
          supplier.location.includes(locationFilter)
        )
      }
      
      if (verifiedOnly) {
        filteredSuppliers = filteredSuppliers.filter(supplier => supplier.verified)
      }
      
      if (minRating > 0) {
        filteredSuppliers = filteredSuppliers.filter(supplier => supplier.rating >= minRating)
      }
      
      await new Promise(resolve => setTimeout(resolve, 500))
      return filteredSuppliers
    },
    enabled: !!user
  })

  const categories = ['all', 'Mobilya', 'Teknoloji', 'Kırtasiye', 'İnşaat', 'Tekstil']
  const locations = ['all', 'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya']

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tedarikçiler</h1>
        <p className="text-gray-600 mt-1">
          Doğrulanmış tedarikçiler ile iş ortaklığı kurun.
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Tedarikçi ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

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

            {/* Location Filter */}
            <select
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="all">Tüm Konumlar</option>
              {locations.filter(loc => loc !== 'all').map((location) => (
                <option key={location} value={location}>
                  {location}
                </option>
              ))}
            </select>

            {/* Rating Filter */}
            <select
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value={0}>Tüm Puanlar</option>
              <option value={4}>4+ Yıldız</option>
              <option value={4.5}>4.5+ Yıldız</option>
              <option value={5}>5 Yıldız</option>
            </select>
          </div>

          {/* Additional Filters */}
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={verifiedOnly}
                onChange={(e) => setVerifiedOnly(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">Sadece Doğrulanmış</span>
            </label>

            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('')
                setCategoryFilter('all')
                setLocationFilter('all')
                setVerifiedOnly(false)
                setMinRating(0)
              }}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Filtreleri Temizle
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {suppliers && suppliers.length > 0 ? (
          suppliers.map((supplier) => (
            <Card key={supplier.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Building className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        {supplier.name}
                        {supplier.verified && (
                          <Shield className="h-4 w-4 text-green-500" title="Doğrulanmış Tedarikçi" />
                        )}
                      </CardTitle>
                      <div className="flex items-center gap-1 mt-1">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium">{supplier.rating}</span>
                        <span className="text-sm text-gray-500">({supplier.reviewCount} değerlendirme)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600 line-clamp-2">
                  {supplier.description}
                </p>

                {/* Categories */}
                <div className="flex flex-wrap gap-1">
                  {supplier.category.map((cat) => (
                    <Badge key={cat} variant="outline" className="text-xs">
                      {cat}
                    </Badge>
                  ))}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-gray-400" />
                    <span>{supplier.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-gray-400" />
                    <span>{supplier.completedOrders} sipariş</span>
                  </div>
                </div>

                {/* Response Time */}
                <div className="text-sm">
                  <span className="text-gray-500">Yanıt süresi: </span>
                  <span className="font-medium">{supplier.responseTime}</span>
                </div>

                {/* Specialties */}
                {supplier.specialties.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-1">Uzmanlık Alanları:</h4>
                    <div className="flex flex-wrap gap-1">
                      {supplier.specialties.slice(0, 2).map((specialty) => (
                        <Badge key={specialty} variant="secondary" className="text-xs">
                          {specialty}
                        </Badge>
                      ))}
                      {supplier.specialties.length > 2 && (
                        <span className="text-xs text-gray-500">
                          +{supplier.specialties.length - 2} daha
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Contact Info */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <a href={`mailto:${supplier.contact.email}`} className="text-blue-600 hover:underline">
                      {supplier.contact.email}
                    </a>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <a href={`tel:${supplier.contact.phone}`} className="text-blue-600 hover:underline">
                      {supplier.contact.phone}
                    </a>
                  </div>
                  {supplier.contact.website && (
                    <div className="flex items-center gap-2 text-sm">
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                      <a 
                        href={supplier.contact.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Web Sitesi
                      </a>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" className="flex-1" size="sm">
                    İletişim
                  </Button>
                  <Button className="flex-1" size="sm">
                    RFQ Gönder
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <Building className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p className="text-gray-500 mb-4">
              {searchTerm || categoryFilter !== 'all' || locationFilter !== 'all' || verifiedOnly || minRating > 0
                ? 'Arama kriterlerinize uygun tedarikçi bulunamadı.'
                : 'Henüz tedarikçi bulunmamaktadır.'
              }
            </p>
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('')
                setCategoryFilter('all')
                setLocationFilter('all')
                setVerifiedOnly(false)
                setMinRating(0)
              }}
            >
              Filtreleri Temizle
            </Button>
          </div>
        )}
      </div>

      {/* Results Count */}
      {suppliers && (
        <div className="text-center text-sm text-gray-500">
          Toplam {suppliers.length} tedarikçi bulundu
        </div>
      )}
    </div>
  )
}
