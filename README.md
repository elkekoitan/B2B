# Agentik B2B Tedarik Uygulaması

## Genel Bakış

Agentik B2B Tedarik Uygulaması, işletmelerin tedarik süreçlerini otomatikleştiren ve optimize eden tam kapsamlı bir B2B platformudur. Uygulama, RFQ (Request for Quotation) yönetimi, tedarikçi keşfi, teklif karşılaştırması ve agent-tabanlı otomasyon özellikleri sunar.

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Docker ve Docker Compose
- Git
- Supabase hesabı
- SMTP e-posta hesabı (Gmail önerilir)

### 1. Projeyi Klonlayın

```bash
git clone <repository-url>
cd agentik-b2b-tedarik
```

### 2. Environment Variables Ayarlayın

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyip Supabase ve email ayarlarınızı girin:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Uygulamayı Başlatın

**Otomatik kurulum (önerilen):**
```bash
chmod +x start.sh
./start.sh
```

**Manuel kurulum:**
```bash
docker-compose build
docker-compose up -d
```

### 4. Uygulamaya Erişim

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Dokumentasyonu**: http://localhost:8000/docs
- **Redis**: localhost:6379

Yeni API Uçları (özet):
- RFQ Şablonları: `GET /api/v1/rfqs/templates`, `GET /api/v1/rfqs/templates/{category}`, `POST /api/v1/rfqs/template`
- Katalog: `GET /api/v1/catalog/mine`, `GET /api/v1/catalog/supplier/{id}`, `POST/PUT/DELETE /api/v1/catalog/*`
- Doğrulama: `POST /api/v1/verification/request`, `POST /api/v1/verification/approve`
- 2FA: `POST /api/v1/auth/2fa/setup|enable|disable`
- Util: `GET /api/v1/utils/currency/rates|convert`

## 📋 Docker Komutları

### Servisleri Başlatma
```bash
docker-compose up -d
```

### Servisleri Durdurma
```bash
docker-compose down
```

### Logları Görüntüleme
```bash
# Tüm servislerin logları
docker-compose logs -f

# Belirli bir servisin logları
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f agent-orchestrator
docker-compose logs -f redis
```

### Servis Durumunu Kontrol Etme
```bash
docker-compose ps
```

### Container'lara Erişim
```bash
# Backend container'ına bağlan
docker-compose exec backend bash

# Database'e erişim (Supabase üzerinden)
docker-compose exec backend python -c "from app.core.database import supabase; print(supabase)"
```

### Yeniden Build Etme
```bash
# Tüm servisleri yeniden build et
docker-compose build --no-cache

# Belirli bir servisi build et
docker-compose build backend
```

## 🏗️ Mimari

### Servis Yapısı

```
┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │    Frontend     │
│  (Port: 80)     │────│   (React)       │
│                 │    │  (Port: 3000)   │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│    Backend      │    │     Redis       │
│   (FastAPI)     │────│  (Message Queue)│
│  (Port: 8000)   │    │  (Port: 6379)   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Supabase      │    │ Agent           │
│  (Database)     │    │ Orchestrator    │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

### Network Yapısı

- **agentik-network**: Tüm servisler arası iletişim
- **Port Mappings**:
  - 80: Nginx (Production)
  - 3000: Frontend (Development)
  - 8000: Backend API
  - 6379: Redis

## Özellikler

- 🔍 **RFQ Yönetimi**: Teklif taleplerinin oluşturulması ve yönetimi
- 🏢 **Tedarikçi Keşfi**: Otomatik tedarikçi bulma ve doğrulama
- 📧 **E-posta Entegrasyonu**: Otomatik e-posta gönderimi ve yanıt işleme
- 📊 **Teklif Karşılaştırması**: Akıllı teklif analizi ve karşılaştırma
- 🤖 **Agent Sistemi**: 6 özelleşmiş AI agent ile süreç otomasyonu
- 🔐 **Güvenlik**: Row Level Security (RLS) ile veri koruması
- 📱 **Responsive**: Tüm cihazlarda mükemmel kullanım deneyimi

## 📈 Proje Takip

Güncel durum, görseller ve yol haritası için `docs/PROJECT_TRACKING.md` ve özet ilerleme için `docs/PROGRESS_OVERVIEW.md` dokümanlarına bakın. Tüm dokümanlar `docs/` klasöründe toplanmıştır (bkz. `docs/README.md`).

## Teknoloji Yığını

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11
- **Database**: Supabase (PostgreSQL)
- **Cache/Queue**: Redis
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Nginx
- **Authentication**: Supabase Auth
- **Email**: SMTP Integration

## Agent Sistemi

6 özelleşmiş AI agent:

1. **RFQ Intake Agent**: RFQ'ları alır ve işler
2. **Supplier Discovery Agent**: Tedarikçileri keşfeder ve listeler
3. **Email Send Agent**: E-postaları gönderir
4. **Inbox Parser Agent**: Gelen e-postaları analiz eder
5. **Supplier Verifier Agent**: Tedarikçileri doğrular
6. **Aggregation & Report Agent**: Sonuçları toplar ve rapor oluşturur

### Agent Workflow

```
RFQ Oluştur → RFQ Intake → Supplier Discovery → Email Send
                                  ↓
Rapor Oluştur ← Aggregation ← Supplier Verifier ← Inbox Parser
```

## 🔧 Geliştirme

### Lokal Geliştirme

```bash
# Backend geliştirme
cd .
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend geliştirme
cd frontend
npm install
npm start

# Agent geliştirme
cd agent_orchestrator
pip install -r requirements.txt
python main.py
```

### Test Etme

```bash
# Backend testleri
docker-compose exec backend pytest

# Frontend testleri
docker-compose exec frontend npm test
```

## 🔒 Güvenlik

- **Row Level Security (RLS)**: Supabase veritabanında kullanıcı bazlı veri erişimi
- **JWT Authentication**: Supabase Auth ile güvenli oturum yönetimi
- **Environment Variables**: Hassas bilgilerin güvenli saklanması

## 🗄️ Veritabanı Şeması

Supabase üzerinde aşağıdaki ek alan ve tablolar gereklidir:
- `companies.verified BOOLEAN DEFAULT FALSE`
- `users.two_factor_secret TEXT`, `users.two_factor_enabled BOOLEAN DEFAULT FALSE`
- Tablo: `supplier_products` (tedarikçi kataloğu)
- Mevcut tablolar: `attachments`, `notifications`, `email_logs`

Migrations klasöründe örnekleri yer alır: `supabase/migrations/*`.
- **CORS**: Cross-origin isteklerin kontrollü yönetimi

## 📊 Monitoring ve Logging

### Log Dosyaları

- Backend: `./logs/backend.log`
- Agent Orchestrator: `./logs/agents.log`
- Nginx: Docker logs üzerinden

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Redis health
redis-cli ping
```

## 🚀 Production Deployment

### SSL Sertifikası

1. SSL sertifikalarını `./ssl/` klasörüne yerleştirin
2. `nginx.conf` dosyasındaki SSL yapılandırmasını aktifleştirin
3. Domain ayarlarını güncelleyin

### Environment Variables

Production ortamında `.env` dosyasını güncelleyin:

```env
ENVIRONMENT=production
# Production Supabase URL'leri
# Production SMTP ayarları
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar

1. **Port zaten kullanımda**:
   ```bash
   docker-compose down
   lsof -ti:3000 | xargs kill -9
   ```

2. **Supabase bağlantı hatası**:
   - `.env` dosyasındaki Supabase ayarlarını kontrol edin
   - Supabase projesinin aktif olduğunu doğrulayın

3. **Redis bağlantı hatası**:
   ```bash
   docker-compose restart redis
   ```

4. **Email gönderimi çalışmıyor**:
   - Gmail için App Password kullandığınızdan emin olun
   - SMTP ayarlarını kontrol edin

### Debug Modları

```bash
# Verbose logging
docker-compose up --remove-orphans

# Belirli servisleri yeniden başlat
docker-compose restart backend agent-orchestrator
```

## 📚 API Dokümantasyonu

Detaylı API dokümantasyonu için: http://localhost:8000/docs

### Temel Endpoints

- `GET /rfqs` - RFQ listesi
- `POST /rfqs` - Yeni RFQ oluştur
- `GET /suppliers` - Tedarikçi listesi
- `POST /orchestrate` - Agent workflow başlat
- `GET /offers` - Teklif listesi

## 📐 Wireframes & Konfigürasyon

- Wireframes: `docs/WIREFRAMES.md` — temel ekran taslakları ve alanlar.
- Konfigürasyon: `docs/CONFIGURATION_GUIDE.md` — ortam değişkenleri ve en iyi uygulamalar.
  - Önemli env: `ALLOWED_ORIGINS` (CORS domain listesi), `PERMISSIONS_ENFORCED` (RBAC’i zorunlu kılar)

## 🤝 Katkıda Bulunma

Katkı rehberi ve proje kuralları için bkz. [AGENTS.md](./AGENTS.md).

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'e push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- Email: support@agentik.com
- GitHub: https://github.com/agentik/b2b-tedarik
- Dokümantasyon: https://docs.agentik.com

---

**Not**: Bu uygulama production kullanımına hazırdır. Herhangi bir sorun yaşarsanız lütfen GitHub Issues bölümünü kullanın.
