import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  FileText, 
  Users, 
  TrendingUp, 
  Shield, 
  Clock, 
  Target,
  ArrowRight,
  CheckCircle,
  Star
} from 'lucide-react'

const features = [
  {
    icon: FileText,
    title: 'RFQ Yönetimi',
    description: 'Kolay ve hızlı RFQ oluşturma, yayınlama ve takip etme.'
  },
  {
    icon: Users,
    title: 'Tedarikçi Ağı',
    description: 'Binlerce doğrulanmış tedarikçiye anında ulaşın.'
  },
  {
    icon: TrendingUp,
    title: 'Teklif Karşılaştırma',
    description: 'Gelen teklifleri kolayca karşılaştırın ve en iyisini seçin.'
  },
  {
    icon: Shield,
    title: 'Güvenli Platform',
    description: 'İş verileriniz bankacılık seviyesinde güvenlikle korunuyor.'
  },
  {
    icon: Clock,
    title: '24/7 Destek',
    description: 'Uzman ekibimiz her zaman size yardımcı olmak için burada.'
  },
  {
    icon: Target,
    title: 'Akıllı Eşleştirme',
    description: 'AI destekli algoritma ile en uygun tedarikçileri bulun.'
  }
]

const testimonials = [
  {
    name: 'Mehmet Kaya',
    company: 'ABC İnşaat',
    text: 'Agentik sayesinde tedarik süreçlerimiz %60 hızlandı. Artık manuel işlemlerle zaman kaybetmiyoruz.',
    rating: 5
  },
  {
    name: 'Ayşe Demir',
    company: 'XYZ Teknoloji',
    text: 'Platform çok kullanışlı. Tek tıkla yüzlerce tedarikçiye ulaşabiliyorum.',
    rating: 5
  },
  {
    name: 'Ali Öztürk',
    company: 'Modern Tekstil',
    text: 'Maliyet tasarrufu sağladığımız gibi, kaliteli tedarikçilerle de tanıştık.',
    rating: 5
  }
]

const stats = [
  { value: '10,000+', label: 'Aktif Kullanıcı' },
  { value: '50,000+', label: 'Tamamlanan RFQ' },
  { value: '5,000+', label: 'Doğrulanmış Tedarikçi' },
  { value: '%98', label: 'Memnuniyet Oranı' }
]

export default function HomePage() {
  const { user } = useAuth()

  // If user is authenticated, redirect to dashboard
  if (user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Hoş geldiniz!
          </h2>
          <Button asChild size="lg">
            <Link to="/app/dashboard">Dashboard'a Git</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                Agentik B2B
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/login" className="text-gray-600 hover:text-gray-900">
                Giriş Yap
              </Link>
              <Button asChild>
                <Link to="/register">Ücretsiz Başla</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-6">
              B2B Tedarik Süreçlerinizi
              <span className="text-blue-600"> Dijitalleştirin</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Agentik ile RFQ'larınızı kolayca yönetin, doğrulanmış tedarikçilerle buluşun 
              ve en iyi teklifleri alın. Tedarik sürecinizi hızlandırın, maliyetleri optimize edin.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="text-lg px-8 py-3" asChild>
                <Link to="/register">
                  Ücretsiz Başlayın
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="text-lg px-8 py-3"
                onClick={() => document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Demo İzle
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Neden Agentik B2B?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Modern teknoloji ile tedarik süreçlerinizi optimize edin, 
              zamandan ve maliyetten tasarruf edin.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-none shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                    <feature.icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Nasıl Çalışır?
            </h2>
            <p className="text-xl text-gray-600">
              3 basit adımda tedarik sürecinizi başlatın
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-blue-500 text-white rounded-full text-2xl font-bold mb-4 mx-auto">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                RFQ Oluşturun
              </h3>
              <p className="text-gray-600">
                İhtiyacınızı detaylandırın ve RFQ'nizi oluşturun. 
                Platforma yükleyin ve tedarikçilere ulaştırın.
              </p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-blue-500 text-white rounded-full text-2xl font-bold mb-4 mx-auto">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Teklifler Alın
              </h3>
              <p className="text-gray-600">
                Doğrulanmış tedarikçilerden rekabetçi teklifler alın. 
                Her teklifi detaylı şekilde inceleyin.
              </p>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-blue-500 text-white rounded-full text-2xl font-bold mb-4 mx-auto">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                En İyisini Seçin
              </h3>
              <p className="text-gray-600">
                Teklifleri karşılaştırın, en uygununu seçin 
                ve tedarikçinizle anlaşmayı tamamlayın.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Müşterilerimiz Ne Diyor?
            </h2>
            <p className="text-xl text-gray-600">
              Binlerce şirket Agentik'i tercih ediyor
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-none shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 mb-4 italic">
                    "{testimonial.text}"
                  </p>
                  <div>
                    <div className="font-semibold text-gray-900">
                      {testimonial.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {testimonial.company}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-6">
            Hazır mısınız? Hemen başlayın!
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Ücretsiz hesap oluşturun ve tedarik süreçlerinizi dijitalleştirmeye başlayın.
            Kredi kartı gerektirmez, anında kullanmaya başlayabilirsiniz.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary" 
              className="text-lg px-8 py-3 text-blue-600"
              asChild
            >
              <Link to="/register">
                Ücretsiz Hesap Oluştur
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="text-lg px-8 py-3 text-white border-white hover:bg-white hover:text-blue-600"
              onClick={() => window.open('https://cal.com/agentik', '_blank')}
            >
              Demo Talep Et
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="text-2xl font-bold text-blue-400 mb-4">
                Agentik B2B
              </div>
              <p className="text-gray-400">
                B2B tedarik süreçlerini dijitalleştiren 
                yenilikçi platform.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/features" className="hover:text-white">Özellikler</Link></li>
                <li><Link to="/pricing" className="hover:text-white">Fiyatlandırma</Link></li>
                <li><Link to="/security" className="hover:text-white">Güvenlik</Link></li>
                <li><Link to="/api" className="hover:text-white">API</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Destek</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/help" className="hover:text-white">Yardım Merkezi</Link></li>
                <li><Link to="/contact" className="hover:text-white">İletişim</Link></li>
                <li><Link to="/status" className="hover:text-white">Sistem Durumu</Link></li>
                <li><Link to="/updates" className="hover:text-white">Güncellemeler</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Yasal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/terms" className="hover:text-white">Kullanım Koşulları</Link></li>
                <li><Link to="/privacy" className="hover:text-white">Gizlilik Politikası</Link></li>
                <li><Link to="/cookies" className="hover:text-white">Çerez Politikası</Link></li>
                <li><Link to="/gdpr" className="hover:text-white">KVKK</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Agentik B2B. Tüm hakları saklıdır.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
