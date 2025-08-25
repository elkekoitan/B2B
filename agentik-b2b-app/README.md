# Agentik B2B Tedarik Uygulaması

**AI destekli B2B tedarik zinciri yönetim platformu**

Agentik B2B, yapay zeka ve otomasyon teknolojilerini kullanarak işletmelerin tedarik süreçlerini optimize eden, modern bir B2B procurement platformudur.

## 🚀 Özellikler

### 🎯 Core Özellikler
- **Akıllı RFQ Yönetimi**: AI destekli RFQ oluşturma ve yönetimi
- **Otomatik Tedarikçi Keşfi**: Uygun tedarikçileri otomatik bulma ve eşleştirme
- **Intelligent Email Automation**: Otomatik e-posta gönderimi ve takibi
- **Smart Inbox Parsing**: Gelen e-postaları otomatik analiz etme
- **Tedarikçi Doğrulama**: Otomatik tedarikçi kredibilite kontrolü
- **Analiz ve Raporlama**: Kapsamlı performans analizi ve iş zekası

### 🏗️ Teknik Özellikler
- **Event-Driven Architecture**: Mikroservis tabanlı olay güdümlü mimari
- **Real-time Processing**: Redis ile gerçek zamanlı veri işleme
- **Scalable Backend**: FastAPI ile yüksek performanslı API
- **Modern Frontend**: React + TypeScript + TailwindCSS
- **AI Agent System**: 6 özelleşmiş AI agent ile otomasyon
- **Docker Support**: Tek komut ile deployment

## 🏛️ Mimari

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄───┤   (FastAPI)     │◄───┤   (Supabase)    │
│   Port: 3000    │    │   Port: 8000    │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent         │    │   Redis         │    │   Email         │
│   Orchestrator  │◄───┤   Queue         │    │   Service       │
│   Port: 8001    │    │   Port: 6379    │    │   (SMTP)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🤖 AI Agent Sistemi

1. **RFQ Intake Agent**: RFQ'ları işler ve zenginleştirir
2. **Supplier Discovery Agent**: Uygun tedarikçileri keşfeder ve davet gönderir
3. **Email Send Agent**: Tüm e-posta iletişimlerini yönetir
4. **Inbox Parser Agent**: Gelen e-postaları analiz eder
5. **Supplier Verifier Agent**: Tedarikçi doğrulama işlemlerini gerçekleştirir
6. **Aggregation Report Agent**: Veri analizi ve raporlama yapar

## 🚀 Kurulum

### Önkoşullar
- Docker & Docker Compose
- Node.js 18+ (geliştirme için)
- Python 3.11+ (geliştirme için)
- Supabase hesabı

### 1. Repository'yi klonlayın
```bash
git clone <repository-url>
cd agentik-b2b-app
```

### 2. Environment variables'ları ayarlayın
```bash
# Ana .env dosyasını oluşturun
cp .env.example .env

# Backend için
cp backend/.env.example backend/.env

# Frontend için
cp agentik-frontend/.env.example agentik-frontend/.env
```

### 3. Environment dosyalarını düzenleyin

**.env** (Ana dosya):
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

### 4. Supabase kurulumu
1. [Supabase](https://supabase.com) hesabı oluşturun
2. Yeni proje oluşturun
3. Veritabanı tablolarını oluşturun (SQL dosyaları `docs/` klasöründe)

### 5. Aplikasyonu başlatın
```bash
# Tüm servisleri Docker ile başlat
docker-compose up -d

# Veya geliştirme modunda
docker-compose -f docker-compose.dev.yml up -d
```

### 6. Uygulamaya erişin
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Agent Orchestrator**: http://localhost:8001

## 📱 Kullanım

### Temel İş Akışı

1. **Hesap Oluşturma**
   - Platform'a kayıt olun
   - Şirket bilgilerinizi girin
   - E-posta doğrulaması yapın

2. **RFQ Oluşturma**
   - Dashboard'dan "Yeni RFQ" butonuna tıklayın
   - RFQ detaylarını doldurun
   - Dosya eklerini yükleyin
   - RFQ'yu yayınlayın

3. **Otomatik Süreç**
   - AI sistem uygun tedarikçileri bulur
   - Otomatik davetler gönderilir
   - Teklifler analiz edilir
   - Karşılaştırma raporları oluşturulur

4. **Teklif Değerlendirme**
   - Gelen teklifleri karşılaştırın
   - AI önerilerini inceleyin
   - En uygun teklifi seçin
   - Sözleşme sürecini başlatın

### Supplier (Tedarikçi) Özellikleri

- **Supplier Profili**: Detaylı şirket profili oluşturma
- **RFQ Bildirimleri**: Uygun RFQ'lar için otomatik bildirimler
- **Teklif Yönetimi**: Teklifleri oluşturma ve yönetme
- **Performans Takibi**: Başarı metriklerini izleme

## 🔧 Geliştirme

### Geliştirme Ortamı Kurulumu

```bash
# Backend geliştirme
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend geliştirme
cd agentik-frontend
pnpm install
pnpm dev

# Agent sistemi geliştirme
cd agents
pip install -r requirements.txt
python main.py
```

### Kod Yapısı

```
agentik-b2b-app/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Pydantic models
│   │   └── services/       # Business logic
│   └── requirements.txt
├── agentik-frontend/        # React Frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   └── lib/           # Utilities
│   └── package.json
├── agents/                  # AI Agent System
│   ├── agents/             # Individual agents
│   ├── core/              # Agent infrastructure
│   └── main.py            # Agent orchestrator
├── docker-compose.yml       # Production deployment
└── README.md
```

### API Dokümantasyonu

Backend çalışırken http://localhost:8000/docs adresinden interaktif API dokümantasyonuna erişebilirsiniz.

**Ana Endpoint'ler:**
- `POST /api/v1/auth/register` - Kullanıcı kaydı
- `GET /api/v1/rfqs` - RFQ listesi
- `POST /api/v1/rfqs` - Yeni RFQ oluşturma
- `GET /api/v1/suppliers` - Tedarikçi listesi
- `POST /api/v1/offers` - Teklif gönderme

### Agent API'leri

```bash
# Agent durumunu kontrol etme
curl http://localhost:8001/agents/status

# Manuel agent tetikleme
curl -X POST http://localhost:8001/trigger-agent/rfq_intake_agent \
  -H "Content-Type: application/json" \
  -d '{"action": "process_rfq", "rfq_id": "123"}'
```

## 🔒 Güvenlik

### Implemented Security Measures
- **Row Level Security (RLS)**: Supabase ile veri erişim kontrolü
- **JWT Authentication**: Güvenli kullanıcı doğrulaması
- **API Key Protection**: Hassas API anahtarlarının korunması
- **Environment Variables**: Konfigürasyon güvenliği
- **CORS Protection**: Cross-origin isteği kontrolü

### Güvenlik Best Practices
- Tüm API anahtarlarını `.env` dosyalarında saklayın
- Production'da güçlü `SECRET_KEY` kullanın
- Düzenli güvenlik güncellemeleri yapın
- Database backup'larını düzenli alın

## 📊 Monitoring & Analytics

### Sistem Metrikleri
- **RFQ Performance**: RFQ başarı oranları
- **Supplier Engagement**: Tedarikçi katılım metrikleri  
- **Email Delivery**: E-posta teslimat oranları
- **Agent Performance**: AI agent performans analizi
- **Response Times**: Sistem yanıt süreleri

### Raporlar
- Günlük sistem raporları
- RFQ analiz raporları
- Tedarikçi performans raporları
- Pazar trend analizleri

## 🐳 Docker Deployment

### Production Deployment

```bash
# Production build
docker-compose -f docker-compose.yml up -d --build

# Logları kontrol etme
docker-compose logs -f

# Specific servis logları
docker-compose logs -f backend
docker-compose logs -f agent-orchestrator
```

### Scaling

```bash
# Agent servislerini scale etme
docker-compose up -d --scale agent-orchestrator=3

# Backend API'yi scale etme
docker-compose up -d --scale backend=2
```

## 🚨 Troubleshooting

### Yaygın Sorunlar

**1. Database Connection Error**
```bash
# Supabase bağlantı bilgilerini kontrol edin
docker-compose logs postgres
```

**2. Redis Connection Error**
```bash
# Redis servisini yeniden başlatın
docker-compose restart redis
```

**3. Email Sending Issues**
- SMTP bilgilerini kontrol edin
- Gmail için App Password kullanın
- Firewall ayarlarını kontrol edin

**4. Agent Not Processing Tasks**
```bash
# Agent loglarını kontrol edin
docker-compose logs agent-orchestrator

# Redis queue'yu kontrol edin
docker exec -it agentik-redis redis-cli
> LLEN agent_rfq_intake_agent_queue
```

## 🤝 Contributing

1. Fork the repository
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 License

Bu proje [MIT License](LICENSE) altında lisanslanmıştır.

## 🙏 Teşekkürler

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [Supabase](https://supabase.com/) - Backend-as-a-Service
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Redis](https://redis.io/) - In-memory data structure store

## 📞 İletişim

Sorularınız için:
- Email: info@agentik-b2b.com
- GitHub Issues: Bu repository'deki issue tracker'ı kullanın

---

**Agentik B2B** - AI ile desteklenen geleceğin tedarik zinciri yönetimi ✨