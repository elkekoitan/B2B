import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function AuthCallbackPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('Auth callback error:', error)
          toast.error('Doğrulama sırasında hata oluştu: ' + error.message)
          navigate('/login', { replace: true })
          return
        }
        
        if (data?.session) {
          toast.success('E-posta başarıyla doğrulandı!')
          const returnUrl = searchParams.get('returnUrl') || '/app/dashboard'
          navigate(returnUrl, { replace: true })
        } else {
          toast.error('Doğrulama başarısız oldu')
          navigate('/login', { replace: true })
        }
      } catch (error: any) {
        console.error('Auth callback error:', error)
        toast.error('Doğrulama sırasında hata oluştu')
        navigate('/login', { replace: true })
      }
    }
    
    handleAuthCallback()
  }, [navigate, searchParams])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mx-auto mb-4" />
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          Hesabınız doğrulanıyor...
        </h2>
        <p className="text-gray-600">
          Lütfen bekleyiniz, bu işlem birkaç saniye sürebilir.
        </p>
      </div>
    </div>
  )
}
