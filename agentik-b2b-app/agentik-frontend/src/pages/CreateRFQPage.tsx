import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

// Form validation schema
const rfqFormSchema = z.object({
  title: z.string().min(5, 'Başlık en az 5 karakter olmalıdır').max(100, 'Başlık en fazla 100 karakter olabilir'),
  description: z.string().min(20, 'Açıklama en az 20 karakter olmalıdır'),
  company: z.string().min(2, 'Şirket adı gereklidir'),
  category: z.string().min(1, 'Kategori seçimi gereklidir'),
  productSpecs: z.string().min(10, 'Ürün/hizmet detayları gereklidir'),
  quantity: z.string().min(1, 'Miktar gereklidir'),
  unit: z.string().min(1, 'Birim seçimi gereklidir'),
  deadline: z.string().min(1, 'Son teslim tarihi gereklidir'),
  budget: z.string().optional(),
  deliveryLocation: z.string().min(5, 'Teslimat adresi gereklidir'),
  specialRequirements: z.string().optional(),
  contactPerson: z.string().min(2, 'İletişim kişisi gereklidir'),
  contactEmail: z.string().email('Geçerli bir e-posta adresi giriniz'),
  contactPhone: z.string().min(10, 'Geçerli bir telefon numarası giriniz')
})

type RFQFormData = z.infer<typeof rfqFormSchema>

const categories = [
  { value: 'office_supplies', label: 'Büro Malzemeleri' },
  { value: 'it_equipment', label: 'IT Ekipmanları' },
  { value: 'furniture', label: 'Mobilya' },
  { value: 'construction', label: 'İnşaat Malzemeleri' },
  { value: 'automotive', label: 'Otomotiv' },
  { value: 'textile', label: 'Tekstil' },
  { value: 'food', label: 'Gıda' },
  { value: 'electronics', label: 'Elektronik' },
  { value: 'services', label: 'Hizmetler' },
  { value: 'other', label: 'Diğer' }
]

const units = [
  { value: 'piece', label: 'Adet' },
  { value: 'kg', label: 'Kilogram' },
  { value: 'meter', label: 'Metre' },
  { value: 'liter', label: 'Litre' },
  { value: 'box', label: 'Kutu' },
  { value: 'set', label: 'Set' },
  { value: 'service', label: 'Hizmet' }
]

export default function CreateRFQPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [isDraft, setIsDraft] = useState(false)
  const [attachments, setAttachments] = useState<File[]>([])

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    getValues
  } = useForm<RFQFormData>({
    resolver: zodResolver(rfqFormSchema),
    mode: 'onChange',
    defaultValues: {
      company: user?.user_metadata?.company_name || '',
      contactPerson: user?.user_metadata?.full_name || '',
      contactEmail: user?.email || ''
    }
  })

  // Create RFQ mutation
  const createRFQMutation = useMutation({
    mutationFn: async (data: RFQFormData & { status: 'draft' | 'published', attachments: File[] }) => {
      return await apiClient.createRFQ(data)
    },
    onSuccess: (data, variables) => {
      const status = variables.status
      toast.success(
        status === 'draft' ? 'RFQ taslak olarak kaydedildi' : 'RFQ başarıyla yayınlandı'
      )
      navigate(`/app/rfqs/${data.id}`)
    },
    onError: (error) => {
      toast.error(`RFQ oluşturulurken hata oluştu: ${error.message}`)
    }
  })

  // Save as draft
  const handleSaveDraft = () => {
    const formData = getValues()
    if (!formData.title || !formData.description) {
      toast.error('En az başlık ve açıklama girilmelidir')
      return
    }
    
    setIsDraft(true)
    createRFQMutation.mutate({
      ...formData,
      status: 'draft',
      attachments
    })
  }

  // Publish RFQ
  const handlePublish = (data: RFQFormData) => {
    setIsDraft(false)
    createRFQMutation.mutate({
      ...data,
      status: 'published',
      attachments
    })
  }

  // File upload handler
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    
    // Validate file types and size
    const validFiles = files.filter(file => {
      const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      const maxSize = 10 * 1024 * 1024 // 10MB
      
      if (!validTypes.includes(file.type)) {
        toast.error(`${file.name}: Desteklenmeyen dosya türü`)
        return false
      }
      
      if (file.size > maxSize) {
        toast.error(`${file.name}: Dosya boyutu çok büyük (max 10MB)`)
        return false
      }
      
      return true
    })
    
    setAttachments(prev => [...prev, ...validFiles])
  }

  // Remove attachment
  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const isLoading = createRFQMutation.isPending

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="border-b pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Yeni RFQ Oluştur</h1>
        <p className="text-gray-600 mt-1">
          Tedarikçilerden teklif almak için RFQ (Request for Quote) oluşturun.
        </p>
      </div>

      <form onSubmit={handleSubmit(handlePublish)} className="space-y-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Temel Bilgiler</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="title">RFQ Başlığı *</Label>
                <Input
                  {...register('title')}
                  id="title"
                  placeholder="Örn: Büro Mobilyası Tedariki"
                  className={errors.title ? 'border-red-500' : ''}
                />
                {errors.title && (
                  <p className="text-sm text-red-600 mt-1">{errors.title.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="category">Kategori *</Label>
                <select
                  {...register('category')}
                  id="category"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Kategori Seçiniz</option>
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="text-sm text-red-600 mt-1">{errors.category.message}</p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="description">Açıklama *</Label>
              <textarea
                {...register('description')}
                id="description"
                rows={4}
                placeholder="RFQ'nızı detaylı bir şekilde açıklayınız..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              {errors.description && (
                <p className="text-sm text-red-600 mt-1">{errors.description.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="company">Şirket Adı *</Label>
              <Input
                {...register('company')}
                id="company"
                placeholder="Şirket adınız"
                className={errors.company ? 'border-red-500' : ''}
              />
              {errors.company && (
                <p className="text-sm text-red-600 mt-1">{errors.company.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Product/Service Details */}
        <Card>
          <CardHeader>
            <CardTitle>Ürün/Hizmet Detayları</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="productSpecs">Ürün/Hizmet Detayları *</Label>
              <textarea
                {...register('productSpecs')}
                id="productSpecs"
                rows={4}
                placeholder="İhtiyaç duyduğunuz ürün veya hizmetin detaylı özelliklerini yazınız..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              {errors.productSpecs && (
                <p className="text-sm text-red-600 mt-1">{errors.productSpecs.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="quantity">Miktar *</Label>
                <Input
                  {...register('quantity')}
                  id="quantity"
                  type="number"
                  placeholder="100"
                  className={errors.quantity ? 'border-red-500' : ''}
                />
                {errors.quantity && (
                  <p className="text-sm text-red-600 mt-1">{errors.quantity.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="unit">Birim *</Label>
                <select
                  {...register('unit')}
                  id="unit"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Birim Seçiniz</option>
                  {units.map((unit) => (
                    <option key={unit.value} value={unit.value}>
                      {unit.label}
                    </option>
                  ))}
                </select>
                {errors.unit && (
                  <p className="text-sm text-red-600 mt-1">{errors.unit.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="budget">Bütçe (İsteğe Bağlı)</Label>
                <Input
                  {...register('budget')}
                  id="budget"
                  type="number"
                  placeholder="10000"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Timeline and Location */}
        <Card>
          <CardHeader>
            <CardTitle>Zaman ve Konum</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="deadline">Son Teslim Tarihi *</Label>
                <Input
                  {...register('deadline')}
                  id="deadline"
                  type="datetime-local"
                  className={errors.deadline ? 'border-red-500' : ''}
                />
                {errors.deadline && (
                  <p className="text-sm text-red-600 mt-1">{errors.deadline.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="deliveryLocation">Teslimat Adresi *</Label>
                <Input
                  {...register('deliveryLocation')}
                  id="deliveryLocation"
                  placeholder="İstanbul, Türkiye"
                  className={errors.deliveryLocation ? 'border-red-500' : ''}
                />
                {errors.deliveryLocation && (
                  <p className="text-sm text-red-600 mt-1">{errors.deliveryLocation.message}</p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="specialRequirements">Özel Gereksinimler</Label>
              <textarea
                {...register('specialRequirements')}
                id="specialRequirements"
                rows={3}
                placeholder="Varsa özel taleplerinizi yazınız..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle>İletişim Bilgileri</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="contactPerson">İletişim Kişisi *</Label>
                <Input
                  {...register('contactPerson')}
                  id="contactPerson"
                  placeholder="Ad Soyad"
                  className={errors.contactPerson ? 'border-red-500' : ''}
                />
                {errors.contactPerson && (
                  <p className="text-sm text-red-600 mt-1">{errors.contactPerson.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="contactEmail">E-posta *</Label>
                <Input
                  {...register('contactEmail')}
                  id="contactEmail"
                  type="email"
                  placeholder="ornek@sirket.com"
                  className={errors.contactEmail ? 'border-red-500' : ''}
                />
                {errors.contactEmail && (
                  <p className="text-sm text-red-600 mt-1">{errors.contactEmail.message}</p>
                )}
              </div>

              <div>
                <Label htmlFor="contactPhone">Telefon *</Label>
                <Input
                  {...register('contactPhone')}
                  id="contactPhone"
                  placeholder="+90 555 123 4567"
                  className={errors.contactPhone ? 'border-red-500' : ''}
                />
                {errors.contactPhone && (
                  <p className="text-sm text-red-600 mt-1">{errors.contactPhone.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* File Attachments */}
        <Card>
          <CardHeader>
            <CardTitle>Ekler</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="attachments">Dosya Ekle</Label>
              <Input
                id="attachments"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                onChange={handleFileUpload}
                className="cursor-pointer"
              />
              <p className="text-sm text-gray-500 mt-1">
                PDF, Word, JPG, PNG formatlarında, dosya başına maksimum 10MB
              </p>
            </div>

            {/* Attachment List */}
            {attachments.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium">Eklenen Dosyalar:</h4>
                {attachments.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm">{file.name}</span>
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      onClick={() => removeAttachment(index)}
                    >
                      Kaldır
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={handleSaveDraft}
            disabled={isLoading}
          >
            {isLoading && isDraft && <LoadingSpinner size="sm" className="mr-2" />}
            Taslak Olarak Kaydet
          </Button>
          
          <Button
            type="submit"
            disabled={!isValid || isLoading}
          >
            {isLoading && !isDraft && <LoadingSpinner size="sm" className="mr-2" />}
            RFQ'yu Yayınla
          </Button>
        </div>
      </form>
    </div>
  )
}
