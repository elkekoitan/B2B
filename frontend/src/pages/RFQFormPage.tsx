import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useApiClient } from '../services/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Textarea } from '../components/ui/Textarea'
import { Card, CardHeader, CardContent, CardTitle } from '../components/ui/Card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/Select'
import { AlertCircle, CheckCircle, Plus, X } from 'lucide-react'

interface RFQFormData {
  title: string
  description: string
  category: string
  quantity: number
  unit: string
  budget_min?: number
  budget_max?: number
  deadline: string
  delivery_location: string
  requirements?: string
  priority?: string
}

const categories = [
  'Electronics',
  'Machinery',
  'Chemicals',
  'Textiles',
  'Food & Beverage',
  'Automotive',
  'Construction',
  'Medical',
  'Other'
]

const units = [
  'pieces',
  'kg',
  'tons',
  'liters',
  'meters',
  'boxes',
  'packages',
  'sets',
  'units'
]

const priorities = [
  { value: 'low', label: 'Düşük' },
  { value: 'medium', label: 'Orta' },
  { value: 'high', label: 'Yüksek' }
]

export function RFQFormPage() {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<RFQFormData>()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)
  const navigate = useNavigate()
  const apiClient = useApiClient()

  const onSubmit = async (data: RFQFormData) => {
    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      // Format data for backend
      const formattedData = {
        ...data,
        deadline: new Date(data.deadline).toISOString(),
        priority: data.priority || 'medium'
      }
      
      // Create RFQ
      const response = await apiClient.createRFQ(formattedData)
      
      if (response.success && response.data?.rfq) {
        const rfqId = response.data.rfq.id
        setSuccess(true)
        
        // Start agent workflow
        try {
          const workflowResponse = await apiClient.startWorkflow({
            job_type: 'rfq_process',
            rfq_id: rfqId,
            payload: {
              rfq: response.data.rfq
            }
          })
          
          if (workflowResponse.success && workflowResponse.data?.job_id) {
            setJobId(workflowResponse.data.job_id)
          }
        } catch (workflowError) {
          console.error('Failed to start workflow:', workflowError)
        }
        
        // Redirect after 3 seconds
        setTimeout(() => {
          navigate('/dashboard')
        }, 3000)
      } else {
        throw new Error(response.message || 'RFQ creation failed')
      }
    } catch (err: any) {
      setError(err.message || 'RFQ oluşturulurken hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (date: Date) => {
    return date.toISOString().slice(0, 16)
  }

  const minDate = formatDateTime(new Date(Date.now() + 24 * 60 * 60 * 1000)) // Tomorrow
  const maxDate = formatDateTime(new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)) // 1 year from now

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full">
          <CardContent className="text-center py-8">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              RFQ Başarıyla Oluşturuldu!
            </h2>
            <p className="text-gray-600 mb-4">
              RFQ'nuz oluşturuldu ve tedarikçi arama süreci başlatıldı.
            </p>
            {jobId && (
              <p className="text-sm text-gray-500 mb-4">
                İş Takip No: {jobId}
              </p>
            )}
            <p className="text-sm text-gray-500">
              Dashboard'a yönlendiriliyorsunuz...
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Yeni RFQ Oluştur
            </CardTitle>
            <p className="text-gray-600">
              Tedarikçilerden teklif almak için RFQ'nuz için gerekli bilgileri doldurun.
            </p>
          </CardHeader>

          <CardContent>
            {error && (
              <div className="flex items-center gap-2 p-4 mb-6 bg-red-50 border border-red-200 rounded-md">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    RFQ Başlığı *
                  </label>
                  <Input
                    {...register('title', { 
                      required: 'Başlık zorunludur',
                      minLength: { value: 3, message: 'Başlık en az 3 karakter olmalıdır' }
                    })}
                    placeholder="Örnek: 1000 adet Elektronik Komponent Tedariki"
                  />
                  {errors.title && (
                    <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kategori *
                  </label>
                  <Select onValueChange={(value) => setValue('category', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Kategori seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category.toLowerCase()}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.category && (
                    <p className="text-red-500 text-sm mt-1">{errors.category.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Teslimat Lokasyonu *
                  </label>
                  <Input
                    {...register('delivery_location', { required: 'Teslimat lokasyonu zorunludur' })}
                    placeholder="Şehir, Ülke"
                  />
                  {errors.delivery_location && (
                    <p className="text-red-500 text-sm mt-1">{errors.delivery_location.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Öncelik Durumu
                  </label>
                  <Select onValueChange={(value) => setValue('priority', value)} defaultValue="medium">
                    <SelectTrigger>
                      <SelectValue placeholder="Öncelik seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      {priorities.map((priority) => (
                        <SelectItem key={priority.value} value={priority.value}>
                          {priority.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Miktar *
                  </label>
                  <Input
                    type="number"
                    {...register('quantity', { 
                      required: 'Miktar zorunludur',
                      min: { value: 1, message: 'Miktar en az 1 olmalıdır' }
                    })}
                    placeholder="1000"
                  />
                  {errors.quantity && (
                    <p className="text-red-500 text-sm mt-1">{errors.quantity.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Birim *
                  </label>
                  <Select onValueChange={(value) => setValue('unit', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Birim seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      {units.map((unit) => (
                        <SelectItem key={unit} value={unit}>
                          {unit}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.unit && (
                    <p className="text-red-500 text-sm mt-1">{errors.unit.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Son Teklif Tarihi *
                  </label>
                  <Input
                    type="datetime-local"
                    min={minDate}
                    max={maxDate}
                    {...register('deadline', { required: 'Son teklif tarihi zorunludur' })}
                  />
                  {errors.deadline && (
                    <p className="text-red-500 text-sm mt-1">{errors.deadline.message}</p>
                  )}
                </div>
              </div>

              {/* Budget Range */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Bütçe ($)
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    {...register('budget_min', { min: { value: 0, message: 'Bütçe negatif olamaz' } })}
                    placeholder="1000.00"
                  />
                  {errors.budget_min && (
                    <p className="text-red-500 text-sm mt-1">{errors.budget_min.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maksimum Bütçe ($)
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    {...register('budget_max', { min: { value: 0, message: 'Bütçe negatif olamaz' } })}
                    placeholder="5000.00"
                  />
                  {errors.budget_max && (
                    <p className="text-red-500 text-sm mt-1">{errors.budget_max.message}</p>
                  )}
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Detaylı Açıklama *
                </label>
                <Textarea
                  rows={4}
                  {...register('description', { 
                    required: 'Açıklama zorunludur',
                    minLength: { value: 10, message: 'Açıklama en az 10 karakter olmalıdır' }
                  })}
                  placeholder="Ürün/hizmet hakkında detaylı bilgi verin..."
                />
                {errors.description && (
                  <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
                )}
              </div>

              {/* Requirements */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Özel Gereksinimler
                </label>
                <Textarea
                  rows={3}
                  {...register('requirements')}
                  placeholder="Kalite standartları, sertifikalar, özel koşullar..."
                />
              </div>

              {/* Submit Button */}
              <div className="flex justify-end pt-6">
                <Button
                  type="submit"
                  disabled={loading}
                  className="min-w-[200px]"
                >
                  {loading ? 'Oluşturuluyor...' : 'RFQ Oluştur ve Yayınla'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}