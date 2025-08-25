# Agent Sistemi Dokümantasyonu

## Genel Bakış

Agentik B2B platformu, 6 özelleşmiş AI agent ile otomatik iş süreçleri yürütür. Her agent belirli görevlerden sorumludur ve Redis üzerinden event-driven messaging ile haberleşir.

## Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Agent Orchestrator                       │
│                 (Port: 8001)                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Redis Queue                          │
│               (Event Bus)                              │
└─────┬───────┬────────┬────────┬───────┬────────────────┘
      │       │        │        │       │        
      ▼       ▼        ▼        ▼       ▼        
   Agent1  Agent2   Agent3   Agent4  Agent5   Agent6
```

## Agent'lar

### 1. RFQ Intake Agent
**Görevi:** RFQ'ları işler, doğrular ve zenginleştirir.

**Tetiklenme Koşulları:**
- Yeni RFQ oluşturulduğunda
- RFQ yayınlandığında
- Manuel tetikleme

**İşlem Akışı:**
```
1. RFQ verilerini doğrula
2. Eksik bilgileri tamamla
3. Kategori bazlı anahtar kelimeler ekle
4. Aciliyet skoru hesapla
5. Veritabanını güncelle
6. Supplier Discovery Agent'i tetikle
```

**Queue:** `agent_rfq_intake_agent_queue`

**Örnek Task:**
```json
{
  "action": "process_rfq",
  "rfq_id": "uuid",
  "rfq_data": {
    "title": "Elektronik Komponent",
    "category": "Electronics",
    "status": "published"
  }
}
```

### 2. Supplier Discovery Agent  
**Görevi:** RFQ'lara uygun tedarikçileri bulur ve davet gönderir.

**Tetiklenme Koşulları:**
- RFQ Intake Agent tarafından tetiklenir
- Manuel tedarikçi arama istekleri

**İşlem Akışı:**
```
1. RFQ kriterlerine göre tedarikçi ara
2. Tedarikçileri skorla ve sırala  
3. En uygun tedarikçileri seç
4. Davet kayıtları oluştur
5. Email Agent'i tetikle
```

**Skorlama Kriterleri:**
- Tedarikçi rating'i (0-50 puan)
- Tamamlanan sipariş sayısı (0-30 puan)  
- Ortalama yanıt süresi (0-20 puan)
- Doğrulama durumu (+10 bonus)

**Queue:** `agent_supplier_discovery_agent_queue`

### 3. Email Send Agent
**Görevi:** Tüm e-posta iletişimlerini yönetir.

**E-posta Türleri:**
- RFQ davetiyeleri
- Teklif bildirimleri 
- Ödül bildirimleri
- Hoş geldin e-postaları
- Sistem uyarıları

**İşlem Akışı:**
```
1. E-posta türünü belirle
2. İçerik template'ini hazırla
3. SMTP ile e-posta gönder
4. Gönderim durumunu logla
5. Veritabanını güncelle
```

**Queue:** `agent_email_send_agent_queue`

**Örnek Task:**
```json
{
  "action": "send_rfq_invitation",
  "rfq_id": "uuid",
  "supplier_email": "supplier@example.com",
  "supplier_name": "TechCorp",
  "invitation_id": "uuid"
}
```

### 4. Inbox Parser Agent
**Görevi:** Gelen e-postaları analiz eder ve ilgili bilgileri çıkarır.

**Analiz Edilen E-posta Türleri:**
- Teklif bildirimleri
- RFQ yanıtları
- Doğrulama e-postaları
- Genel RFQ iletişimi

**İşlem Akışı:**
```
1. IMAP ile inbox'ı tara
2. Okunmamış e-postaları al
3. İçeriği parse et
4. İlgili bilgileri çıkar (fiyat, teslimat süresi vs.)
5. Veritabanına kaydet
6. Follow-up aksiyonları tetikle
```

**Çıkarılan Veriler:**
- Gönderen bilgileri
- Fiyat teklifleri (regex ile)
- Teslimat süreleri
- Şirket isimleri

**Queue:** `agent_inbox_parser_agent_queue`

### 5. Supplier Verifier Agent
**Görevi:** Tedarikçi bilgilerini doğrular ve güvenilirlik kontrolü yapar.

**Doğrulama Kriterleri:**
- E-posta format kontrolü (15 puan)
- Domain doğrulaması (10 puan)
- Şirket ismi kontrolü (20 puan)
- Vergi numarası doğrulama (10 puan)
- Telefon format kontrolü (10 puan)
- Website erişilebilirliği (15 puan)
- Sektör uyumu (10 puan)
- Uzmanlık alanları (10 puan)

**Doğrulama Skoru:** 0-100 arası
- 70+ → Otomatik doğrulama
- 60-69 → Manuel inceleme
- <60 → Reddedilme

**İşlem Akışı:**
```
1. Tedarikçi bilgilerini al
2. Doğrulama kontrollerini yap
3. Toplam skoru hesapla
4. Doğrulama durumunu güncelle
5. Hoş geldin e-postası gönder (eğer doğrulandıysa)
```

**Queue:** `agent_supplier_verifier_agent_queue`

### 6. Aggregation Report Agent
**Görevi:** Sistem verilerini toplar, analiz eder ve raporlar oluşturur.

**Rapor Türleri:**
- Günlük sistem raporu
- RFQ performans analizi
- Tedarikçi değerlendirmesi
- Pazar analizleri
- Performans metrikleri

**Günlük Sistem Raporu Metrikleri:**
- Toplam RFQ sayısı
- Yayınlanan RFQ sayısı
- Alınan teklif sayısı
- Gönderilen e-posta sayısı
- Yeni tedarikçi sayısı
- Doğrulanan tedarikçi sayısı

**RFQ Analizi:**
- Teklif fiyat analizi (min, max, ortalama, medyan)
- Tedarikçi kalite analizi
- En iyi teklif önerileri
- Optimizasyon tavsiyeleri

**Queue:** `agent_aggregation_report_agent_queue`

## Agent Orchestrator API

### Sağlık Kontrolü
```bash
GET http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Agentik Agent Orchestrator",
  "active_agents": 6
}
```

### Agent Durumu
```bash
GET http://localhost:8001/agents/status
```

**Response:**
```json
{
  "total_agents": 6,
  "agents": [
    {
      "name": "rfq_intake_agent",
      "description": "Processes and validates new RFQ submissions",
      "status": "active"
    }
  ]
}
```

### Manuel Agent Tetikleme
```bash
POST http://localhost:8001/trigger-agent/rfq_intake_agent
Content-Type: application/json

{
  "action": "process_rfq",
  "rfq_id": "uuid",
  "rfq_data": {...}
}
```

## Redis Queue Yönetimi

### Queue İzleme
```bash
# Redis container'a bağlan
docker exec -it agentik-redis redis-cli

# Queue uzunluğunu kontrol et
LLEN agent_rfq_intake_agent_queue

# Queue'daki taskları listele
LRANGE agent_rfq_intake_agent_queue 0 -1

# Tüm queue'ları listele
KEYS agent_*_queue
```

### Manuel Task Ekleme
```bash
# Redis CLI'dan task ekle
LPUSH agent_rfq_intake_agent_queue '{"action":"process_rfq","rfq_id":"test-123"}'
```

## Agent Geliştirme

### Yeni Agent Oluşturma

1. **BaseAgent'tan türet:**
```python
from core.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my_custom_agent",
            description="My custom agent description"
        )
    
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Task processing logic here
        return {"success": True}
```

2. **Orchestrator'a kaydet:**
```python
# main.py içinde
from agents.my_custom_agent import MyCustomAgent

# Register agent
await orchestrator.register_agent(MyCustomAgent())
```

### Agent Best Practices

1. **Error Handling:** Her task için try-catch kullan
2. **Logging:** İşlem adımlarını detaylı logla
3. **Idempotency:** Aynı task tekrar çalıştırılabilir olsun
4. **Resource Management:** Database bağlantılarını düzgün kapat
5. **Task Validation:** Gelen parametreleri doğrula

### Agent Testing

```python
# Test agent locally
import asyncio
from agents.rfq_intake_agent import RFQIntakeAgent

async def test_agent():
    agent = RFQIntakeAgent()
    task_data = {
        "action": "process_rfq",
        "rfq_id": "test-123",
        "rfq_data": {...}
    }
    
    result = await agent.process_task(task_data)
    print(result)

asyncio.run(test_agent())
```

## Monitoring & Debugging

### Log İzleme
```bash
# Tüm agent logları
docker-compose logs -f agent-orchestrator

# Belirli agent logları (grep ile filtrele)
docker-compose logs agent-orchestrator | grep "rfq_intake_agent"
```

### Performance Metrikleri

Agent performansı aşağıdaki metriklerle izlenir:

- **Task Processing Time**: Task işlem süreleri
- **Success Rate**: Başarı oranları
- **Queue Length**: Queue uzunlukları
- **Error Rate**: Hata oranları
- **Throughput**: Saniye başına işlenen task sayısı

### Troubleshooting

**Agent Çalışmıyor:**
1. Agent Orchestrator loglarını kontrol et
2. Redis bağlantısını kontrol et
3. Database bağlantısını kontrol et
4. Environment variables'ları kontrol et

**Task İşlenmiyor:**
1. Queue'da task var mı kontrol et
2. Agent'in doğru queue'yu dinlediğini kontrol et
3. Task format'ının doğru olduğunu kontrol et

**E-posta Gönderilmiyor:**
1. SMTP ayarlarını kontrol et
2. Email Agent loglarını incele
3. Gmail App Password kullanıyor musun kontrol et

## Scaling Agent System

### Horizontal Scaling
```bash
# Agent orchestrator'ı scale et
docker-compose up -d --scale agent-orchestrator=3
```

### Queue Partitioning
Yüksek throughput için queue'ları bölebilirsiniz:
```
agent_rfq_intake_agent_queue_1
agent_rfq_intake_agent_queue_2
agent_rfq_intake_agent_queue_3
```

### Load Balancing
Agent'lar round-robin veya weighted distribution ile task alabilir.

## Future Enhancements

- **Dead Letter Queues**: Başarısız taskları yönetme
- **Task Retries**: Otomatik tekrar deneme mekanizması
- **Priority Queues**: Öncelikli task işleme
- **Circuit Breakers**: Fail-safe mekanizmaları
- **Metrics Dashboard**: Grafana ile görselleştirme
- **AI Integration**: GPT/Claude entegrasyonu için hazırlık