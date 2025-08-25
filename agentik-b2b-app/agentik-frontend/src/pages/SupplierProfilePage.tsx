import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useAuth } from '@/contexts/AuthContext'
import { 
  Building, 
  Star, 
  MapPin, 
  Phone, 
  Mail, 
  Globe, 
  Award,
  Package,
  Truck,
  Shield,
  Edit,
  Save,
  X,
  Plus
} from 'lucide-react'

// Form validation schema
const supplierProfileSchema = z.object({
  companyName: z.string().min(2, 'Şirket adı en az 2 karakter olmalıdır'),
  description: z.string().min(20, 'Açıklama en az 20 karakter olmalıdır'),
  website: z.string().url('Geçerli bir web sitesi adresi giriniz').or(z.literal('')).optional(),
  phone: z.string().min(10, 'Geçerli bir telefon numarası giriniz'),
  email: z.string().email('Geçerli bir e-posta adresi giriniz'),
  address: z.string().min(10, 'Adres en az 10 karakter olmalıdır'),
  city: z.string().min(2, 'Şehir bilgisi gereklidir'),
  country: z.string().min(2, 'Ülke bilgisi gereklidir'),
  foundedYear: z.string().optional(),
  employeeCount: z.string().min(1, 'Çalışan sayısı seçimi gereklidir'),
  annualRevenue: z.string().optional(),
  taxNumber: z.string().min(10, 'Vergi numarası gereklidir'),
  bankAccount: z.string().optional(),
  minimumOrderValue: z.string().optional(),
  averageDeliveryTime: z.string().min(1, 'Ortalama teslimat süresi gereklidir'),
  paymentTerms: z.string().min(1, 'Ödeme koşulları gereklidir'),
  qualityCertificates: z.string().optional(),
  specializations: z.string().optional()
})

type SupplierProfileFormData = z.infer<typeof supplierProfileSchema>

const employeeCounts = [
  { value: '1-10', label: '1-10 kişi' },
  { value: '11-50', label: '11-50 kişi' },
  { value: '51-200', label: '51-200 kişi' },
  { value: '201-500', label: '201-500 kişi' },
  { value: '500+', label: '500+ kişi' }
]

const deliveryTimes = [
  { value: '1-3', label: '1-3 gün' },
  { value: '4-7', label: '4-7 gün' },
  { value: '1-2week', label: '1-2 hafta' },
  { value: '2-4week', label: '2-4 hafta' },
  { value: '1month+', label: '1 ay+' }
]

const paymentTermOptions = [
  { value: 'advance', label: 'Peşin Ödeme' },
  { value: '30days', label: '30 Gün Vadeli' },
  { value: '60days', label: '60 Gün Vadeli' },
  { value: '90days', label: '90 Gün Vadeli' },
  { value: 'custom', label: 'Özel Koşullar' }
]

export default function SupplierProfilePage() {
  const { user } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [categories, setCategories] = useState(['Mobilya', 'Teknoloji'])
  const [newCategory, setNewCategory] = useState('')

  // Mock supplier data - in real app, this would come from API
  const mockSupplierData = {
    companyName: 'Mobilya Pro A.Ş.',
    description: 'Premium kalite büro mobilyaları üretimi ve tedariki konusunda 15 yıllık deneyime sahip, müşteri memnuniyeti odaklı çalışan profesyonel bir firmayız.',
    website: 'https://mobilyapro.com',
    phone: '+90 212 555 0101',
    email: 'info@mobilyapro.com',
    address: 'Organize Sanayi Bölgesi 15. Sok. No: 42',
    city: 'İstanbul',
    country: 'Türkiye',
    foundedYear: '2008',
    employeeCount: '51-200',
    annualRevenue: '10-50M',
    taxNumber: '1234567890',
    bankAccount: 'TR123456789012345678901234',
    minimumOrderValue: '5000',
    averageDeliveryTime: '1-2week',
    paymentTerms: '30days',
    qualityCertificates: 'ISO 9001, TSE, CE',
    specializations: 'Ergonomik Mobilya, Özel Tasarım, Toplu Projeler'
  }

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset
  } = useForm<SupplierProfileFormData>({
    resolver: zodResolver(supplierProfileSchema),
    mode: 'onChange',
    defaultValues: mockSupplierData
  })

  const handleUpdateProfile = async (data: SupplierProfileFormData) => {
    setIsLoading(true)
    
    try {
      // API call to update supplier profile
      // await apiClient.updateSupplierProfile(data)
      
      toast.success('Tedarikçi profili başarıyla güncellendi!')
      setIsEditing(false)
      
    } catch (error: any) {
      toast.error('Profil güncellenirken hata oluştu: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    reset(mockSupplierData)
    setIsEditing(false)
  }

  const addCategory = () => {
    if (newCategory.trim() && !categories.includes(newCategory.trim())) {
      setCategories([...categories, newCategory.trim()])
      setNewCategory('')
    }
  }

  const removeCategory = (category: string) => {
    setCategories(categories.filter(c => c !== category))
  }

  // Mock stats
  const stats = {
    totalRFQs: 45,
    completedOrders: 235,
    rating: 4.8,
    responseTime: '2-4 saat',
    satisfactionRate: 98
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Building className="h-8 w-8" />
            Tedarikçi Profilim
          </h1>
          <p className="text-gray-600 mt-1">
            Tedarikçi profilinizi yönetin ve güncelleyin.
          </p>
        </div>
        
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button 
                variant="outline" 
                onClick={handleCancel}
                disabled={isLoading}
              >
                <X className="h-4 w-4 mr-2" />
                İptal
              </Button>
              <Button 
                onClick={handleSubmit(handleUpdateProfile)}
                disabled={!isValid || isLoading}
              >
                {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
                <Save className="h-4 w-4 mr-2" />
                Kaydet
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)}>
              <Edit className="h-4 w-4 mr-2" />
              Profili Düzenle
            </Button>
          )}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Puan</p>
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 text-yellow-500 fill-current" />
                  <span className="text-xl font-bold">{stats.rating}</span>
                </div>
              </div>
              <Award className="h-6 w-6 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">RFQ Sayısı</p>
                <p className="text-xl font-bold">{stats.totalRFQs}</p>
              </div>
              <Package className="h-6 w-6 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Tamamlanan</p>
                <p className="text-xl font-bold text-green-600">{stats.completedOrders}</p>
              </div>
              <Truck className="h-6 w-6 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Yanıt Süresi</p>
                <p className="text-lg font-bold text-purple-600">{stats.responseTime}</p>
              </div>
              <Shield className="h-6 w-6 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Memnuniyet</p>
                <p className="text-xl font-bold text-indigo-600">{stats.satisfactionRate}%</p>
              </div>
              <Star className="h-6 w-6 text-indigo-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <form onSubmit={handleSubmit(handleUpdateProfile)} className="space-y-6">
        {/* Company Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5" />
              Şirket Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="companyName">Şirket Adı *</Label>
                <Input
                  {...register('companyName')}
                  id="companyName"
                  disabled={!isEditing}
                  className={errors.companyName ? 'border-red-500' : ''}
                />
                {errors.companyName && (
                  <p className="text-sm text-red-600 mt-1">{errors.companyName.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="taxNumber">Vergi Numarası *</Label>
                <Input
                  {...register('taxNumber')}
                  id="taxNumber"
                  disabled={!isEditing}
                  className={errors.taxNumber ? 'border-red-500' : ''}
                />
                {errors.taxNumber && (
                  <p className="text-sm text-red-600 mt-1">{errors.taxNumber.message}</p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="description">Açıklama *</Label>
              <textarea
                {...register('description')}
                id="description"
                rows={3}
                disabled={!isEditing}
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              />
              {errors.description && (
                <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="foundedYear">Kuruluş Yılı</Label>
                <Input
                  {...register('foundedYear')}
                  id="foundedYear"
                  type="number"
                  disabled={!isEditing}
                  placeholder="2008"
                />
              </div>

              <div>
                <Label htmlFor="employeeCount">Çalışan Sayısı *</Label>
                <select
                  {...register('employeeCount')}
                  id="employeeCount"
                  disabled={!isEditing}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {employeeCounts.map((count) => (
                    <option key={count.value} value={count.value}>
                      {count.label}
                    </option>
                  ))}
                </select>
                {errors.employeeCount && (
                  <p className="text-sm text-red-600 mt-1">{errors.employeeCount.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="annualRevenue">Yıllık Ciro (TL)</Label>
                <Input
                  {...register('annualRevenue')}
                  id="annualRevenue"
                  disabled={!isEditing}
                  placeholder="10-50M"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Phone className="h-5 w-5" />
              İletişim Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="phone">Telefon *</Label>
                <Input
                  {...register('phone')}
                  id="phone"
                  type="tel"
                  disabled={!isEditing}
                  className={errors.phone ? 'border-red-500' : ''}
                />
                {errors.phone && (
                  <p className="text-sm text-red-600 mt-1">{errors.phone.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="email">E-posta *</Label>
                <Input
                  {...register('email')}
                  id="email"
                  type="email"
                  disabled={!isEditing}
                  className={errors.email ? 'border-red-500' : ''}
                />
                {errors.email && (
                  <p className="text-sm text-red-600 mt-1">{errors.email.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="website">Web Sitesi</Label>
                <Input
                  {...register('website')}
                  id="website"
                  type="url"
                  disabled={!isEditing}
                  className={errors.website ? 'border-red-500' : ''}
                />
                {errors.website && (
                  <p className="text-sm text-red-600 mt-1">{errors.website.message}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="address">Adres *</Label>
                <Input
                  {...register('address')}
                  id="address"
                  disabled={!isEditing}
                  className={errors.address ? 'border-red-500' : ''}
                />
                {errors.address && (
                  <p className="text-sm text-red-600 mt-1">{errors.address.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="city">Şehir *</Label>
                <Input
                  {...register('city')}
                  id="city"
                  disabled={!isEditing}
                  className={errors.city ? 'border-red-500' : ''}
                />
                {errors.city && (
                  <p className="text-sm text-red-600 mt-1">{errors.city.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Business Terms */}
        <Card>
          <CardHeader>
            <CardTitle>Ticari Koşullar</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="minimumOrderValue">Minimum Sipariş Tutarı (TL)</Label>
                <Input
                  {...register('minimumOrderValue')}
                  id="minimumOrderValue"
                  type="number"
                  disabled={!isEditing}
                  placeholder="5000"
                />
              </div>

              <div>
                <Label htmlFor="averageDeliveryTime">Ortalama Teslimat Süresi *</Label>
                <select
                  {...register('averageDeliveryTime')}
                  id="averageDeliveryTime"
                  disabled={!isEditing}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {deliveryTimes.map((time) => (
                    <option key={time.value} value={time.value}>
                      {time.label}
                    </option>
                  ))}
                </select>
                {errors.averageDeliveryTime && (
                  <p className="text-sm text-red-600 mt-1">{errors.averageDeliveryTime.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="paymentTerms">Ödeme Koşulları *</Label>
                <select
                  {...register('paymentTerms')}
                  id="paymentTerms"
                  disabled={!isEditing}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {paymentTermOptions.map((term) => (
                    <option key={term.value} value={term.value}>
                      {term.label}
                    </option>
                  ))}
                </select>
                {errors.paymentTerms && (
                  <p className="text-sm text-red-600 mt-1">{errors.paymentTerms.message}</p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="bankAccount">Banka Hesap Bilgisi (IBAN)</Label>
              <Input
                {...register('bankAccount')}
                id="bankAccount"
                disabled={!isEditing}
                placeholder="TR123456789012345678901234"
              />
            </div>
          </CardContent>
        </Card>

        {/* Categories and Specializations */}
        <Card>
          <CardHeader>
            <CardTitle>Kategoriler ve Uzmanlık Alanları</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Categories */}
            <div>
              <Label>Hizmet Kategorileri</Label>
              <div className="flex flex-wrap gap-2 mb-2">
                {categories.map((category) => (
                  <Badge 
                    key={category} 
                    variant="secondary" 
                    className="flex items-center gap-1"
                  >
                    {category}
                    {isEditing && (
                      <button
                        type="button"
                        onClick={() => removeCategory(category)}
                        className="ml-1 text-red-500 hover:text-red-700"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
              {isEditing && (
                <div className="flex gap-2">
                  <Input
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    placeholder="Yeni kategori ekle"
                    className="flex-1"
                  />
                  <Button type="button" onClick={addCategory} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="specializations">Uzmanlık Alanları</Label>
                <textarea
                  {...register('specializations')}
                  id="specializations"
                  rows={2}
                  disabled={!isEditing}
                  placeholder="Uzmanlık alanlarınızı virgülle ayırarak yazın"
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <div>
                <Label htmlFor="qualityCertificates">Kalite Sertifikaları</Label>
                <textarea
                  {...register('qualityCertificates')}
                  id="qualityCertificates"
                  rows={2}
                  disabled={!isEditing}
                  placeholder="ISO 9001, TSE, CE gibi sertifikalarınız"
                  className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
