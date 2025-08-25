# FastAPI + Supabase + Redis Backend

## Kurulum

1. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Environment variables'ları ayarlayın:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. Uygulamayı başlatın:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `GET /api/v1/auth/me` - Mevcut kullanıcı bilgileri
- `PUT /api/v1/auth/me` - Kullanıcı bilgilerini güncelle
- `POST /api/v1/auth/logout` - Çıkış yap

### RFQs
- `POST /api/v1/rfqs` - RFQ oluştur
- `GET /api/v1/rfqs` - RFQ listesi
- `GET /api/v1/rfqs/{rfq_id}` - RFQ detayı
- `PUT /api/v1/rfqs/{rfq_id}` - RFQ güncelle
- `DELETE /api/v1/rfqs/{rfq_id}` - RFQ sil
- `POST /api/v1/rfqs/{rfq_id}/publish` - RFQ yayınla

### Suppliers
- `GET /api/v1/suppliers` - Tedarikçi listesi
- `POST /api/v1/suppliers` - Tedarikçi kaydı oluştur
- `GET /api/v1/suppliers/{supplier_id}` - Tedarikçi detayı
- `PUT /api/v1/suppliers/{supplier_id}` - Tedarikçi güncelle

### Offers
- `POST /api/v1/offers` - Teklif oluştur
- `GET /api/v1/offers` - Teklif listesi
- `GET /api/v1/offers/by-rfq/{rfq_id}` - RFQ'ya ait teklifler
- `GET /api/v1/offers/{offer_id}` - Teklif detayı
- `PUT /api/v1/offers/{offer_id}` - Teklif güncelle
- `POST /api/v1/offers/{offer_id}/submit` - Teklif gönder

### Email
- `GET /api/v1/emails/logs` - Email logları
- `POST /api/v1/emails/send-rfq-invitation` - RFQ davetiyesi gönder
- `GET /api/v1/emails/invitations/{rfq_id}` - RFQ davetiyeleri

### Notifications
- `GET /api/v1/notifications` - Bildirimler
- `GET /api/v1/notifications/unread-count` - Okunmamış bildirim sayısı
- `PUT /api/v1/notifications/{id}/read` - Bildirimi okundu işaretle
- `PUT /api/v1/notifications/mark-all-read` - Tüm bildirimleri okundu işaretle

### Orchestrator
- `POST /api/v1/orchestrator/orchestrate` - Agent workflow başlat
- `GET /api/v1/orchestrator/status/{job_id}` - Job durumu sorgula
- `POST /api/v1/orchestrator/cancel/{job_id}` - Job'u iptal et
- `POST /api/v1/orchestrator/workflows/rfq-discovery` - RFQ keşif workflow'u
- `POST /api/v1/orchestrator/workflows/supplier-verification` - Tedarikçi doğrulama workflow'u

## Health Check
- `GET /health` - Temel sağlık kontrolü
- `GET /health/detailed` - Detaylı sağlık kontrolü

## Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

## Features

### ✅ Implemented
- **Supabase Integration**: Full CRUD operations
- **Authentication**: JWT token verification
- **Authorization**: RLS (Row Level Security) enforcement
- **Redis Integration**: Job queue system
- **Error Handling**: Comprehensive error management
- **Logging**: Request/response logging
- **Validation**: Pydantic model validation
- **CORS**: Cross-origin resource sharing
- **Security**: Security headers, rate limiting
- **Health Checks**: Database and Redis connectivity

### 🔧 Production Ready Features
- **Middleware**: Logging, security, rate limiting
- **Exception Handling**: Global exception handlers
- **Environment Configuration**: Environment-based settings
- **API Documentation**: Auto-generated OpenAPI docs
- **Response Models**: Consistent API responses
- **Pagination**: Paginated list responses
- **Filtering**: Search and filter capabilities

## Environment Variables

```bash
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key

# SMTP (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Docker Support

```bash
# Docker build
docker build -t agentik-backend .

# Docker run
docker run -p 8000:8000 --env-file .env agentik-backend
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests (when implemented)
pytest
```
