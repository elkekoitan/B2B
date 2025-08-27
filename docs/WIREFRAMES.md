# Wireframes (Metin Tabanlı Taslaklar)

Bu doküman, temel ekranların hızlı taslaklarını ve veri alanlarını gösterir. Amaç, UI/UX akışını teknik ekip için netleştirmektir.

## 1) Dashboard
- Ögeler: Son RFQ’lar (tablo), Aktif işler (jobs), Bildirimler.
- Aksiyonlar: "Yeni RFQ", "Kataloğa git", "Doğrulama".

```
[Header] [User]
[Cards: RFQs count][Offers count][Suppliers]
[Table: Recent RFQs]
[Table: Recent Jobs]
```

## 2) RFQ Template & RFQ Form
- Template seçimi: `chemicals`, `electronics`, ...
- Form alanları: title, description, category, quantity, unit, deadline, budget_min/max, delivery_location, requirements.
- Aksiyonlar: Kaydet, Yayınla, Orchestrate.

```
[Select Template]
[Form Fields]
[Submit Buttons: Save][Publish][Start Workflow]
```

## 3) RFQ Detail
- Kartlar: RFQ bilgileri, Tedarikçi analizi, Teklifler.
- Aksiyonlar: Karşılaştırma raporu indir, Orchestrate başlat, Sil/düzenle.

## 4) Catalog (Supplier Products)
- List/Filter/Pagination, Ekle/Düzenle/Sil.
- Alanlar: name, category, price, moq, certifications.

## 5) Verification (KYC)
- Doküman yükleme, durum: pending/approved/rejected, admin notu.

## 6) Two-Factor (2FA)
- Setup, enable/disable, backup codes.

## 7) Admin Panel
- Doğrulama talepleri listesi, Onay/Ret + not, Loglar.

## 8) Jobs (Agent Orchestrator)
- Liste: job_id, job_type, status, updated_at.
- Aksiyon: İptal (queued ise), Detay.
