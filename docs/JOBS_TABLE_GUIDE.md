# Jobs Tablosu Rehberi

Backend, job durumlarını isteğe bağlı olarak veritabanına da yazabilir. Aşağıdaki şema önerilir.

## Önerilen Şema (Supabase/Postgres)
```sql
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  company_id UUID,
  rfq_id UUID,
  job_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  result JSONB,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Kullanım Notları
- Backend oluştururken `queued` kaydı ekler; status güncellemelerinde `updated_at` yenilenir.
- Redis tek gerçek zamanlı kaynak; tablo raporlama/iz için ek kolaylık sağlar.
- RLS/policy: kullanıcı kendi job kayıtlarını okuyabilmelidir.

## Uygulama
- SQL dosyasını `supabase/migrations/` altına ekleyin ve `scripts/db_migrate_psql.sh` ile uygulayın.
- Backend konfigürasyonu: Supabase env değişkenleri `.env` içinde tanımlanmalıdır.
