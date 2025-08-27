# Güvenlik En İyi Uygulamaları

## Kimlik Doğrulama
- Production’da Supabase JWKS ile JWT imza doğrulaması yapın (aud doğrulaması opsiyonel).
- Geliştirmede yalnızca `mock-admin-token` kullanın; prod’da kapatın.

## CORS
- Prod’da `allow_origins` için net domain listesi kullanın. `*` kullanmayın.

## Secrets & Config
- Secrets’ı `.env` dışında saklayın (CI/CD Secrets). `.env.example`’da örnekleyin ama değer koymayın.
- SMTP ve Supabase anahtarlarına erişimi sınırlayın.

## Veri
- RLS (Row Level Security) politikalarını aktif tutun.
- Jobs tablosunda kullanıcılar yalnızca kendi kayıtlarını görsün.

## Ağ & Log
- Nginx reverse proxy ile HTTPS kullanın (SSL/Let’s Encrypt). 
- Log’larda PII’yi maskeleyin; prod’da debug kapalı olsun.
