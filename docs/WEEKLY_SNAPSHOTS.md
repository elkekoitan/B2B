# 🗓️ Weekly Snapshots

Kısa, tarihlenmiş özetler: ne tamamlandı, ne riskli, sırada ne var.

## 2025-08-25
- Docs: `PROJECT_TRACKING.md` görseller ve repo ağacı eklendi, `docs/README.md` indeks iyileştirildi.
- Governance: PR/Issue şablonları eklendi.
- Plans: `MILESTONE_DASHBOARD.md` ile milestone görünürlüğü sağlandı.
- Next: Catalog UI cilası, entegrasyon testleri (catalog update/delete, verification approve), orchestrator health genişletme.
- Risks: CI çalışma dizini güncel repo yapısıyla uyumlu değil olabilir; doğrulanmalı.

## 2025-08-26
- Infra: Nginx reverse proxy host portu 8080; smoke komutu eklendi (`make smoke`).
- API: Lokal orchestrate uçları eklendi (`POST /orchestrate`, `GET /orchestrate/status/{job_id}`).
- Frontend: Catalog sayfasına kategori/para birimi filtreleri.
- Next: Orchestrator job-history UI (durum görüntüleme) + son smoke senaryoları.

Şablon (kopyala/yapıştır):
```
## YYYY-MM-DD
- Completed: …
- In Progress: …
- Next: …
- Risks/Blocks: …
```
