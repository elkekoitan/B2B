# Documentation Index

Bu dizin, dokümanları kolay ve hızlı erişim için gruplar. Görsel proje yapısı ve kısayollar en altta.

## Kılavuzlar
- Architecture: `SYSTEM_ARCHITECTURE.md`
- API: `API_DOCUMENTATION.md`
- Feature Specs: `FEATURE_SPECIFICATIONS.md`
- Technical Guide: `TECHNICAL_IMPLEMENTATION_GUIDE.md`
- User Manual: `USER_MANUAL.md`
- Roadmap: `B2B_AGENTIK_DEVELOPMENT_ROADMAP.md`
- Contributor Guide: `../AGENTS.md`
- Contributing Process: `CONTRIBUTING.md`
- Security Policy: `SECURITY.md`
- Security Best Practices: `SECURITY_BEST_PRACTICES.md`
- Project Tracking: `PROJECT_TRACKING.md`
- Progress Overview: `PROGRESS_OVERVIEW.md`
- Legacy Reports: `reports/`
- Queue Contract: `QUEUE_CONTRACT.md`
- Jobs Table Guide: `JOBS_TABLE_GUIDE.md`
 - Wireframes: `WIREFRAMES.md`
 - Configuration: `CONFIGURATION_GUIDE.md`

## Hızlı Komutlar
- Servisleri başlat: `make up`
- Logları izle: `make logs`
- Test/Lint: `make test-backend`, `make lint`, `make fmt`, `make ci`
  
- Backend dokümanları: `http://localhost:8000/docs`
- Sağlık kontrolü: `http://localhost:8000/health`
- Reverse proxy: `http://localhost:8080` (API: `/api/*`)
- Smoke test: `make smoke`
- Reverse proxy (Nginx): `http://localhost:8080` (API: `/api/*`)

## Depo Yapısı (Özet)
```
.
├─ app/                 # FastAPI backend
├─ agent_orchestrator/  # Agent orkestratörü
├─ frontend/            # React + Vite + TypeScript
├─ supabase/            # SQL migrasyonları
├─ scripts/             # Yardımcı scriptler
├─ docs/                # Dokümanlar
├─ docker-compose*.yml  # Compose dosyaları
└─ Makefile             # Geliştirme komutları
```

İlerlemenin görsel özeti ve ayrıntılı görev listesi için `PROJECT_TRACKING.md` dosyasına bakın.
