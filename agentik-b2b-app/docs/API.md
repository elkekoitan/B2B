# API Dokümantasyonu

## Base URL
```
Production: https://api.agentik-b2b.com
Development: http://localhost:8000
```

## Authentication

Tüm korumalı endpoint'ler Bearer token gerektirir:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /api/v1/auth/register
Yeni kullanıcı kaydı

**Request Body:**
```json
{
  "auth_user_id": "uuid",
  "company_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "phone": "+90532xxxxxxx"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User profile created successfully",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### GET /api/v1/auth/profile
Kullanıcı profili getir

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company": {
      "name": "Example Corp",
      "industry": "Technology"
    }
  }
}
```

### RFQs

#### GET /api/v1/rfqs
RFQ listesi getir

**Query Parameters:**
- `page` (int): Sayfa numarası (default: 1)
- `per_page` (int): Sayfa başına item (default: 20)
- `status` (string): RFQ durumu filtreleme
- `category` (string): Kategori filtreleme
- `search` (string): Arama terimi

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Elektronik Komponent Tedariki",
      "description": "Detailed description",
      "status": "published",
      "category": "Electronics",
      "created_at": "2025-01-20T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false
}
```

#### POST /api/v1/rfqs
Yeni RFQ oluştur

**Request Body:**
```json
{
  "title": "Elektronik Komponent Tedariki",
  "description": "We need electronic components for our new product line",
  "category": "Electronics",
  "quantity": 1000,
  "unit": "Adet",
  "budget_min": 10000,
  "budget_max": 50000,
  "deadline_date": "2025-02-15",
  "delivery_location": "Istanbul, Turkey",
  "priority": "medium",
  "requirements": {
    "quality_standards": "ISO 9001",
    "certifications": "CE marked",
    "technical_specs": "Detailed technical specifications"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "RFQ başarıyla oluşturuldu",
  "data": {
    "id": "uuid",
    "title": "Elektronik Komponent Tedariki",
    "status": "draft"
  }
}
```

#### GET /api/v1/rfqs/{rfq_id}
RFQ detayı getir

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Elektronik Komponent Tedariki",
    "description": "Detailed description",
    "status": "published",
    "offer_count": 5,
    "average_offer_price": 30000,
    "lowest_offer_price": 25000,
    "highest_offer_price": 35000,
    "company": {
      "name": "Example Corp"
    }
  }
}
```

### Suppliers

#### GET /api/v1/suppliers
Tedarikçi listesi

**Query Parameters:**
- `page` (int): Sayfa numarası
- `per_page` (int): Sayfa başına item
- `specialization` (string): Uzmanlık alanı filtreleme
- `verified_only` (bool): Sadece doğrulanmış tedarikçiler
- `search` (string): Arama terimi

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "rating": 4.5,
      "verified": true,
      "specializations": ["Electronics", "Manufacturing"],
      "companies": {
        "name": "TechSupply Corp",
        "email": "info@techsupply.com"
      }
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20
}
```

#### POST /api/v1/suppliers/profile
Tedarikçi profili oluştur

**Request Body:**
```json
{
  "company_id": "uuid",
  "specializations": ["Electronics", "Components"],
  "certifications": ["ISO 9001", "CE"]
}
```

#### GET /api/v1/suppliers/profile
Mevcut tedarikçi profili

### Offers

#### GET /api/v1/offers
Teklif listesi

**Query Parameters:**
- `page` (int): Sayfa numarası
- `per_page` (int): Sayfa başına item
- `rfq_id` (uuid): Belirli RFQ için teklifler
- `status` (string): Teklif durumu

#### POST /api/v1/offers
Yeni teklif oluştur

**Request Body:**
```json
{
  "rfq_id": "uuid",
  "supplier_id": "uuid",
  "price": 28000,
  "currency": "USD",
  "delivery_time": 15,
  "delivery_terms": "FOB Istanbul",
  "warranty_terms": "2 years",
  "payment_terms": "30 days",
  "technical_specs": {
    "specifications": "Detailed technical specs"
  },
  "notes": "Additional notes",
  "valid_until": "2025-02-01"
}
```

#### GET /api/v1/offers/{offer_id}
Teklif detayı

### Notifications

#### GET /api/v1/notifications
Bildirim listesi

**Query Parameters:**
- `page` (int): Sayfa numarası
- `per_page` (int): Sayfa başına item  
- `unread_only` (bool): Sadece okunmamış bildirimler

#### PUT /api/v1/notifications/{notification_id}/read
Bildirimi okundu olarak işaretle

#### PUT /api/v1/notifications/mark-all-read
Tüm bildirimleri okundu olarak işaretle

#### GET /api/v1/notifications/unread-count
Okunmamış bildirim sayısı

## Error Responses

Tüm hatalar standart format ile döner:

```json
{
  "success": false,
  "message": "Error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "Field specific error"
  }
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

- **General API**: 100 requests per minute per user
- **File Upload**: 10 requests per minute per user
- **Email Sending**: 50 emails per hour per user

## Pagination

Listeleme endpoint'lerinde standart pagination:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

## Webhook Events

Sistem önemli olaylarda webhook gönderir:

### RFQ Events
- `rfq.created` - Yeni RFQ oluşturuldu
- `rfq.published` - RFQ yayınlandı
- `rfq.closed` - RFQ kapatıldı

### Offer Events
- `offer.submitted` - Yeni teklif geldi
- `offer.accepted` - Teklif kabul edildi
- `offer.rejected` - Teklif reddedildi

### Webhook Payload
```json
{
  "event": "rfq.created",
  "timestamp": "2025-01-20T10:00:00Z",
  "data": {
    "rfq_id": "uuid",
    "company_id": "uuid",
    "title": "RFQ Title"
  }
}
```