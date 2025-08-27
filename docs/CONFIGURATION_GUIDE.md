# Konfigürasyon Rehberi

Bu rehber, backend, frontend ve orchestrator servisleri için gerekli ortam değişkenlerini ve en iyi uygulamayı özetler.

## Ortam Dosyaları
- Örnek: `.env.example` → `.env`

## Gerekli Değişkenler
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- Redis: `REDIS_URL` (docker-compose ile otomatik `redis://redis:6379`)
- SMTP: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- Genel: `ENVIRONMENT` (`development` / `production`)
  - CORS: `ALLOWED_ORIGINS` (virgülle ayrılmış), yoksa prod’da domain belirtin.
  - RBAC: `PERMISSIONS_ENFORCED=true` ile endpoint bazlı izin zorunlu kılınır.
- Frontend (Vite): `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`

## En İyi Uygulamalar
- Production’da `CORS` kaynaklarını domainlerle sınırlandırın; wildcard kullanmayın.
- Secrets’ı commit etmeyin; GitHub Actions için repo secrets kullanın.
- `ENVIRONMENT=production` iken JWKS ile JWT doğrulaması aktif olmalı.
- Migration’ları `supabase/migrations/` altına ekleyin; script ile uygulayın.
 - Mocks kullanılmaz: Supabase ve Redis bağlantıları zorunludur.

## Hızlı Kontrol
- `make up` → servisleri başlatır.
- `make logs` → logları izler.
- `make ci` → lint + test.
