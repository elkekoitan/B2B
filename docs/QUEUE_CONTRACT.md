# Kuyruk Sözleşmesi (Backend ↔ Agents)

Bu doküman, Backend (FastAPI) ile Agent Orchestrator arasındaki Redis tabanlı iş akışı sözleşmesini tanımlar.

## Anahtar İsimleri
- Ana kuyruk: `agentik:jobs`
- Ajan kuyrukları: `agentik:agent:{agent_adi}` (örn. `agentik:agent:rfq_intake`)
- İş durumu: `agentik:status:{job_id}` (Redis Hash)

## Job Payload Şeması
```json
{
  "job_id": "<uuid>",
  "job_type": "rfq_process|supplier_discovery|email_campaign",
  "user_id": "<uuid>",
  "rfq_id": "<uuid|null>",
  "payload": { "rfq": { /* RFQ alanları */ }, "...": "..." },
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Durum Hash Alanları
- `status`: `queued|in_progress|completed|failed`
- `created_at`, `updated_at`: ISO-8601
- `result`: JSON (stringleştirilmiş)
- `error`: metin (isteğe bağlı)

## Akış
1. Backend `agentik:jobs` kuyruğuna job yazar.
2. Orchestrator işi `rfq_intake` kuyruğuna yollar; ajanlar aşama aşama işler.
3. Her ajan, `agentik:status:{job_id}` üzerinde `status/result` günceller ve bir sonraki ajana iletir.

## Uygulama İpuçları
- Backend status okurken `result` alanını JSON parse etmeyi unutmayın.
- Ajanlar başarısızlıkta `status=failed` ve `error` doldurmalıdır.
- Kimlik doğrulama için `user_id` zorunludur; yetkisiz statü okumayı engelleyin.
