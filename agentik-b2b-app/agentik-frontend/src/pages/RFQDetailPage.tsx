import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { 
  Calendar, 
  MapPin, 
  User, 
  Phone, 
  Mail,
  FileText,
  Package,
  Building,
  Clock,
  DollarSign
} from 'lucide-react'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

interface RFQ {
  id: string
  title: string
  description: string
  company: string
  category: string
  status: 'draft' | 'published' | 'closed' | 'awarded'
  productSpecs: string
  quantity: number
  unit: string
  deadline: string
  budget?: number
  deliveryLocation: string
  specialRequirements?: string
  contactPerson: string
  contactEmail: string
  contactPhone: string
  attachments: Array<{
    id: string
    name: string
    url: string
  }>
  createdAt: string
  updatedAt: string
}

const statusLabels = {
  draft: { label: 'Taslak', variant: 'outline' as const },
  published: { label: 'Yayında', variant: 'default' as const },
  closed: { label: 'Kapalı', variant: 'secondary' as const },
  awarded: { label: 'İhale Edildi', variant: 'destructive' as const }
}

export default function RFQDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()

  // Fetch RFQ details
  const { data: rfq, isLoading } = useQuery({
    queryKey: ['rfq', id],
    queryFn: async () => {
      // Mock data for now - replace with actual API call
      const mockRFQ: RFQ = {
        id: id!,
        title: 'Büro Mobilyası Tedariki',
        description: 'Yeni ofisimiz için 50 kişilik büro mobilyası setine ihtiyacımız bulunmaktadır.',
        company: 'ABC Şirketi',
        category: 'furniture',
        status: 'published',
        productSpecs: 'Ofis sandalyesi, çalışma masası ve dolap takımları',
        quantity: 50,
        unit: 'set',
        deadline: '2025-02-15T00:00:00Z',
        budget: 150000,
        deliveryLocation: 'İstanbul, Türkiye',
        specialRequirements: 'Montaj hizmeti dahil olmalıdır',
        contactPerson: 'Ahmet Yılmaz',
        contactEmail: 'ahmet@abcsirket.com',
        contactPhone: '+90 212 555 0123',
        attachments: [
          {
            id: '1',
            name: 'Ofis Planı.pdf',
            url: '#'
          }
        ],
        createdAt: '2025-01-01T10:00:00Z',
        updatedAt: '2025-01-05T15:30:00Z'
      }
      
      return mockRFQ
    },
    enabled: !!id
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!rfq) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">RFQ bulunamadı.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b pb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{rfq.title}</h1>
            <p className="text-gray-600 mt-2">{rfq.description}</p>
            <div className="flex items-center gap-4 mt-4">
              <Badge variant={statusLabels[rfq.status].variant}>
                {statusLabels[rfq.status].label}
              </Badge>
              <span className="text-sm text-gray-500">
                ID: {rfq.id}
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Oluşturulma</p>
            <p className="font-medium">
              {format(new Date(rfq.createdAt), 'dd MMM yyyy', { locale: tr })}
            </p>
          </div>
        </div>
      </div>

      {/* RFQ Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Product Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Ürün Detayları
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Ürün Özellikleri</h4>
                <p className="text-gray-600">{rfq.productSpecs}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-700 mb-1">Miktar</h4>
                  <p className="text-gray-600">{rfq.quantity} {rfq.unit}</p>
                </div>
                {rfq.budget && (
                  <div>
                    <h4 className="font-medium text-gray-700 mb-1">Bütçe</h4>
                    <p className="text-gray-600">{rfq.budget.toLocaleString('tr-TR')} TL</p>
                  </div>
                )}
              </div>

              {rfq.specialRequirements && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Özel Gereksinimler</h4>
                  <p className="text-gray-600">{rfq.specialRequirements}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Attachments */}
          {rfq.attachments.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Ekler
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {rfq.attachments.map((attachment) => (
                    <div key={attachment.id} className="flex items-center gap-3 p-3 border rounded-lg">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <span className="text-sm">{attachment.name}</span>
                      <Button variant="outline" size="sm" className="ml-auto">
                        İndir
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Key Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-5 w-5" />
                Temel Bilgiler
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Calendar className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">Son Tarih</p>
                  <p className="text-sm text-gray-600">
                    {format(new Date(rfq.deadline), 'dd MMM yyyy', { locale: tr })}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <MapPin className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">Teslimat Yeri</p>
                  <p className="text-sm text-gray-600">{rfq.deliveryLocation}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Building className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">Şirket</p>
                  <p className="text-sm text-gray-600">{rfq.company}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                İletişim
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <User className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">İletişim Kişisi</p>
                  <p className="text-sm text-gray-600">{rfq.contactPerson}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">E-posta</p>
                  <p className="text-sm text-gray-600">{rfq.contactEmail}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Phone className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">Telefon</p>
                  <p className="text-sm text-gray-600">{rfq.contactPhone}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          {rfq.status === 'published' && (
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-3">
                  <Button className="w-full">
                    Teklif Ver
                  </Button>
                  <Button variant="outline" className="w-full">
                    Soru Sor
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
