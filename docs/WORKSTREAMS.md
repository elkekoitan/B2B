# Workstreams & Active Scope

Bu belge, hangi klasörde hangi işlerin yürütüldüğünü ve mevcut odak alanını netleştirir. Kısa, operasyonel ve günlük takibe uygundur.

## Aktif Odak (Şimdi)
- Klasör: `app/` (FastAPI Backend)
- Hedef: API stabilizasyonu, küçük uç noktalar ve smoke doğrulama
- Neden: Orchestration ve UI’nin sağlıklı çalışabilmesi için API’nin net ve izlenebilir olması gerekiyor.

Rehber Dokümanlar (kaynak-otorite):
- Scope ve sprint takibi: `docs/PROJECT_TRACKING.md`
- Özellik tanımları ve kabul ölçütleri: `docs/API_DOCUMENTATION.md`, `docs/QUEUE_CONTRACT.md`
- Yol haritası referansı: `docs/B2B_AGENTIK_DEVELOPMENT_ROADMAP.md`

## İkincil Odak (Yakın)
- Klasör: `agent_orchestrator/`
- Hedef: Kuyruk sağlık metrikleri, basit telemetri ve akış görünürlüğü
- Neden: İşlerin kuyrukta nerede takıldığını hızlı görmek ve debug hızını artırmak.

## Bekleyen/Cila (Sonraki)
- Klasör: `frontend/`
- Hedef: Katalog sayfası düzenleme/paginasyon/filtre, validasyon ve toast’lar
- Neden: Temel API akışları doğrulandıktan sonra UX cilası daha hızlı ve sağlam yapılır.

---

## Bugünün İşleri (Backend `app/`)
1) Sağlık ve bilgi uçları
   - `/health` doğrulama (Supabase/Redis metrikleri)
   - `/api/v1/info` eklendi (smoke script’in kullandığı basit bilgi)
2) RFQ CRUD tutarlılığı
   - `GET /rfqs/{rfq_id}` route eklendi (RBAC ile)
3) Smoke doğrulama
   - Script: `scripts/smoke_api.sh` (Backend/Proxy/Frontend temel kontroller)

## Yakın Sonraki Adımlar
- Orchestrator metriklerini genişlet: `/orchestrate/queues` ve `/orchestrate/heartbeat` ile görünürlük
- Backend testlerini toparla: RFQ detail ve orchestrate happy-path için hızlı testler
- Frontend’e küçük entegrasyon: `/analytics/jobs` verileriyle basit istatistik kartı

## Bugün Eklenenler
- Orchestrator Heartbeat: `agent_orchestrator/` içinde periyodik heartbeat (Redis `agentik:heartbeat`)
- Backend Uçları: `GET /orchestrate/queues`, `GET /orchestrate/heartbeat`

---

## Dosya / Klasör Haritası (Operasyonel)
- Backend: `app/` – ana entry `app/main.py` (burayı güçlendiriyoruz)
- Orchestrator: `agent_orchestrator/` – `main.py`, `orchestrator.py`, `utils.py`
- Frontend: `frontend/` – Vite+React; `.env`’ler docker compose ile geçer
- Doküman: `docs/` – bu belge ve mimari/API belgeleri
- Scriptler: `scripts/` – `smoke_api.sh`, `db_migrate_psql.sh` vb.

## Nasıl Koşuyoruz
- Docker: `make up` → API `http://localhost:8000`, Proxy `http://localhost:8080`
- Smoke: `bash scripts/smoke_api.sh`
- Backend Dev: `make backend-dev` (hot-reload)

## Notlar
- Kimlik/RBAC: Geliştirmede `Bearer mock-admin-token` desteklenir.
- Ortam değişkenleri: `.env.example`’e bakın; Supabase/Redis/SMTP gerekir.
