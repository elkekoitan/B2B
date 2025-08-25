import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useAuth } from '@/contexts/AuthContext'
import { User, Building, Mail, Phone, MapPin, Edit, Save, X } from 'lucide-react'

// Form validation schema
const profileSchema = z.object({
  fullName: z.string().min(2, 'Ad soyad en az 2 karakter olmalıdır'),
  email: z.string().email('Geçerli bir e-posta adresi giriniz'),
  phone: z.string().optional(),
  companyName: z.string().min(2, 'Şirket adı en az 2 karakter olmalıdır'),
  companySize: z.string().min(1, 'Şirket büyüklüğü seçimi gereklidir'),
  industry: z.string().min(1, 'Sektör seçimi gereklidir'),
  role: z.string().min(1, 'Rol seçimi gereklidir'),
  address: z.string().optional(),
  website: z.string().url('Geçerli bir web sitesi adresi giriniz').or(z.literal('')).optional(),
  taxNumber: z.string().optional(),
  description: z.string().optional()
})

type ProfileFormData = z.infer<typeof profileSchema>

const companySizes = [
  { value: '1-10', label: '1-10 kişi' },
  { value: '11-50', label: '11-50 kişi' },
  { value: '51-200', label: '51-200 kişi' },
  { value: '201-500', label: '201-500 kişi' },
  { value: '500+', label: '500+ kişi' }
]

const industries = [
  { value: 'technology', label: 'Teknoloji' },
  { value: 'manufacturing', label: 'İmalat' },
  { value: 'retail', label: 'Perakende' },
  { value: 'construction', label: 'İnşaat' },
  { value: 'automotive', label: 'Otomotiv' },
  { value: 'healthcare', label: 'Sağlık' },
  { value: 'finance', label: 'Finans' },
  { value: 'education', label: 'Eğitim' },
  { value: 'food', label: 'Gıda' },
  { value: 'other', label: 'Diğer' }
]

const roles = [
  { value: 'owner', label: 'Şirket Sahibi' },
  { value: 'ceo', label: 'CEO' },
  { value: 'manager', label: 'Müdür' },
  { value: 'procurement', label: 'Satın Alma Uzmanı' },
  { value: 'operations', label: 'Operasyon Uzmanı' },
  { value: 'other', label: 'Diğer' }
]

export default function ProfilePage() {
  const { user, updateProfile } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Mock user data - in real app, this would come from user profile
  const mockProfile = {
    fullName: user?.user_metadata?.full_name || 'Ahmet Yılmaz',
    email: user?.email || 'ahmet@abcsirket.com',
    phone: user?.user_metadata?.phone || '+90 555 123 4567',
    companyName: user?.user_metadata?.company_name || 'ABC Şirketi',
    companySize: user?.user_metadata?.company_size || '11-50',
    industry: user?.user_metadata?.industry || 'technology',
    role: user?.user_metadata?.role || 'manager',
    address: user?.user_metadata?.address || 'İstanbul, Türkiye',
    website: user?.user_metadata?.website || 'https://abcsirket.com',
    taxNumber: user?.user_metadata?.tax_number || '1234567890',
    description: user?.user_metadata?.description || 'Teknoloji sektöründe faaliyet gösteren, yenilikçi çözümler üreten dinamik bir şirket.'
  }

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    mode: 'onChange',
    defaultValues: mockProfile
  })

  const handleUpdateProfile = async (data: ProfileFormData) => {
    setIsLoading(true)
    
    try {
      const { error } = await updateProfile({
        full_name: data.fullName,
        phone: data.phone,
        company_name: data.companyName,
        company_size: data.companySize,
        industry: data.industry,
        role: data.role,
        address: data.address,
        website: data.website,
        tax_number: data.taxNumber,
        description: data.description
      })
      
      if (error) {
        toast.error('Profil güncellenemedi: ' + error.message)
        return
      }
      
      toast.success('Profil başarıyla güncellendi!')
      setIsEditing(false)
      
    } catch (error: any) {
      toast.error('Profil güncellenirken hata oluştu: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    reset(mockProfile)
    setIsEditing(false)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Profil Ayarları</h1>
          <p className="text-gray-600 mt-1">
            Hesap bilgilerinizi ve şirket detaylarınızı yönetin.
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
              Düzenle
            </Button>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit(handleUpdateProfile)} className="space-y-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Kişisel Bilgiler
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="fullName">Ad Soyad</Label>
                <Input
                  {...register('fullName')}
                  id="fullName"
                  disabled={!isEditing}
                  className={errors.fullName ? 'border-red-500' : ''}
                />
                {errors.fullName && (
                  <p className="text-sm text-red-600 mt-1">{errors.fullName.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="email">E-posta Adresi</Label>
                <Input
                  {...register('email')}
                  id="email"
                  type="email"
                  disabled // Email cannot be changed via profile
                  className="bg-gray-50"
                />
                <p className="text-xs text-gray-500 mt-1">
                  E-posta adresinizi değiştirmek için destek ekibiyle iletişime geçin.
                </p>
              </div>
            </div>

            <div>
              <Label htmlFor="phone">Telefon</Label>
              <Input
                {...register('phone')}
                id="phone"
                type="tel"
                disabled={!isEditing}
                placeholder="+90 555 123 4567"
              />
            </div>
          </CardContent>
        </Card>

        {/* Company Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5" />
              Şirket Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="companyName">Şirket Adı</Label>
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

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="companySize">Şirket Büyüklüğü</Label>
                <select
                  {...register('companySize')}
                  id="companySize"
                  disabled={!isEditing}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {companySizes.map((size) => (
                    <option key={size.value} value={size.value}>
                      {size.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="industry">Sektör</Label>
                <select
                  {...register('industry')}
                  id="industry"
                  disabled={!isEditing}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {industries.map((industry) => (
                    <option key={industry.value} value={industry.value}>
                      {industry.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="role">Rolünüz</Label>
                <select
                  {...register('role')}
                  id="role"
                  disabled={!isEditing}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {roles.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="website">Web Sitesi</Label>
                <Input
                  {...register('website')}
                  id="website"
                  type="url"
                  disabled={!isEditing}
                  placeholder="https://sirketim.com"
                  className={errors.website ? 'border-red-500' : ''}
                />
                {errors.website && (
                  <p className="text-sm text-red-600 mt-1">{errors.website.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="taxNumber">Vergi Numarası</Label>
                <Input
                  {...register('taxNumber')}
                  id="taxNumber"
                  disabled={!isEditing}
                  placeholder="1234567890"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="address">Adres</Label>
              <Input
                {...register('address')}
                id="address"
                disabled={!isEditing}
                placeholder="Şirket adresiniz"
              />
            </div>

            <div>
              <Label htmlFor="description">Şirket Açıklaması</Label>
              <textarea
                {...register('description')}
                id="description"
                rows={3}
                disabled={!isEditing}
                placeholder="Şirketiniz hakkında kısa açıklama..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          </CardContent>
        </Card>

        {/* Account Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Hesap İstatistikleri</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">12</p>
                <p className="text-sm text-gray-600">Toplam RFQ</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">35</p>
                <p className="text-sm text-gray-600">Alınan Teklif</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">8</p>
                <p className="text-sm text-gray-600">Tamamlanan</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-orange-600">18</p>
                <p className="text-sm text-gray-600">Aktif Tedarikçi</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
