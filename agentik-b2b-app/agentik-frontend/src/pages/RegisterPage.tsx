import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
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
import { Eye, EyeOff, Building, User } from 'lucide-react'

// Form validation schema
const registerSchema = z.object({
  email: z.string().email('Geçerli bir e-posta adresi giriniz'),
  password: z.string().min(8, 'Şifre en az 8 karakter olmalıdır')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Şifre en az bir büyük harf, küçük harf ve rakam içermelidir'),
  confirmPassword: z.string(),
  fullName: z.string().min(2, 'Ad soyad en az 2 karakter olmalıdır'),
  companyName: z.string().min(2, 'Şirket adı en az 2 karakter olmalıdır'),
  companySize: z.string().min(1, 'Şirket büyüklüğü seçimi gereklidir'),
  industry: z.string().min(1, 'Sektör seçimi gereklidir'),
  role: z.string().min(1, 'Rol seçimi gereklidir'),
  phone: z.string().optional(),
  termsAccepted: z.boolean().refine(val => val === true, 'Kullanım koşullarını kabul etmelisiniz')
}).refine((data) => data.password === data.confirmPassword, {
  message: "Şifreler eşleşmiyor",
  path: ["confirmPassword"]
})

type RegisterFormData = z.infer<typeof registerSchema>

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

export default function RegisterPage() {
  const { signUp, user } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const returnUrl = searchParams.get('returnUrl') || '/app/dashboard'

  // Redirect if already logged in
  if (user) {
    navigate(returnUrl, { replace: true })
    return null
  }

  const {
    register,
    handleSubmit,
    formState: { errors, isValid }
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    mode: 'onChange'
  })

  const handleRegister = async (data: RegisterFormData) => {
    setIsLoading(true)
    
    try {
      const userData = {
        full_name: data.fullName,
        company_name: data.companyName,
        company_size: data.companySize,
        industry: data.industry,
        role: data.role,
        phone: data.phone || ''
      }
      
      const { error } = await signUp(data.email, data.password, userData)
      
      if (error) {
        toast.error('Kayıt başarısız: ' + error.message)
        return
      }
      
      toast.success('Kayıt başarıyla tamamlandı! E-postanızı kontrol edin.')
      // Note: User will be redirected after email confirmation
      
    } catch (error: any) {
      toast.error('Kayıt olunurken hata oluştu: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo */}
        <Link to="/" className="flex justify-center">
          <h1 className="text-3xl font-bold text-blue-600">Agentik B2B</h1>
        </Link>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Ücretsiz hesap oluşturun
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Zaten hesabınız var mı?{' '}
          <Link
            to={`/login${returnUrl ? `?returnUrl=${encodeURIComponent(returnUrl)}` : ''}`}
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            Giriş yapın
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Hesap Oluştur</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(handleRegister)} className="space-y-6">
              {/* Personal Information */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-lg font-medium text-gray-900">
                  <User className="h-5 w-5" />
                  Kişisel Bilgiler
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="fullName">Ad Soyad *</Label>
                    <Input
                      {...register('fullName')}
                      id="fullName"
                      placeholder="Adınız Soyadınız"
                      className={errors.fullName ? 'border-red-500' : ''}
                    />
                    {errors.fullName && (
                      <p className="mt-1 text-sm text-red-600">{errors.fullName.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="email">E-posta Adresi *</Label>
                    <Input
                      {...register('email')}
                      id="email"
                      type="email"
                      placeholder="ornek@sirket.com"
                      className={errors.email ? 'border-red-500' : ''}
                    />
                    {errors.email && (
                      <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="password">Şifre *</Label>
                    <div className="relative">
                      <Input
                        {...register('password')}
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Güçlü bir şifre oluşturun"
                        className={errors.password ? 'border-red-500 pr-10' : 'pr-10'}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4 text-gray-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {errors.password && (
                      <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="confirmPassword">Şifre Tekrar *</Label>
                    <div className="relative">
                      <Input
                        {...register('confirmPassword')}
                        id="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        placeholder="Şifrenizi tekrar giriniz"
                        className={errors.confirmPassword ? 'border-red-500 pr-10' : 'pr-10'}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4 text-gray-400" />
                        ) : (
                          <Eye className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {errors.confirmPassword && (
                      <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor="phone">Telefon</Label>
                  <Input
                    {...register('phone')}
                    id="phone"
                    type="tel"
                    placeholder="+90 555 123 4567"
                  />
                </div>
              </div>

              {/* Company Information */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-lg font-medium text-gray-900">
                  <Building className="h-5 w-5" />
                  Şirket Bilgileri
                </div>

                <div>
                  <Label htmlFor="companyName">Şirket Adı *</Label>
                  <Input
                    {...register('companyName')}
                    id="companyName"
                    placeholder="Şirket adınız"
                    className={errors.companyName ? 'border-red-500' : ''}
                  />
                  {errors.companyName && (
                    <p className="mt-1 text-sm text-red-600">{errors.companyName.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="companySize">Şirket Büyüklüğü *</Label>
                    <select
                      {...register('companySize')}
                      id="companySize"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="">Seçiniz</option>
                      {companySizes.map((size) => (
                        <option key={size.value} value={size.value}>
                          {size.label}
                        </option>
                      ))}
                    </select>
                    {errors.companySize && (
                      <p className="mt-1 text-sm text-red-600">{errors.companySize.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="industry">Sektör *</Label>
                    <select
                      {...register('industry')}
                      id="industry"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="">Seçiniz</option>
                      {industries.map((industry) => (
                        <option key={industry.value} value={industry.value}>
                          {industry.label}
                        </option>
                      ))}
                    </select>
                    {errors.industry && (
                      <p className="mt-1 text-sm text-red-600">{errors.industry.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="role">Rolünüz *</Label>
                    <select
                      {...register('role')}
                      id="role"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="">Seçiniz</option>
                      {roles.map((role) => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </select>
                    {errors.role && (
                      <p className="mt-1 text-sm text-red-600">{errors.role.message}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Terms and Conditions */}
              <div className="flex items-center">
                <input
                  {...register('termsAccepted')}
                  id="termsAccepted"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="termsAccepted" className="ml-2 block text-sm text-gray-900">
                  <Link to="/terms" className="text-blue-600 hover:text-blue-500">Kullanım Koşulları</Link>'nı ve{' '}
                  <Link to="/privacy" className="text-blue-600 hover:text-blue-500">Gizlilik Politikası</Link>'nı kabul ediyorum *
                </label>
              </div>
              {errors.termsAccepted && (
                <p className="text-sm text-red-600">{errors.termsAccepted.message}</p>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={!isValid || isLoading}
              >
                {isLoading && <LoadingSpinner size="sm" className="mr-2" />}
                Hesap Oluştur
              </Button>
            </form>

            {/* Social Registration */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Veya</span>
                </div>
              </div>

              <div className="mt-6">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => toast.info('Google ile kayıt yakında eklenecek!')}
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  Google ile Kayıt Ol
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
