# B2B Agentik Platform API Documentation

## Overview

The B2B Agentik Platform provides a comprehensive REST API built with FastAPI, enabling seamless integration for procurement, supplier management, and RFQ processing. This documentation covers all available endpoints, authentication, request/response formats, and integration examples.

**Base URL:** `http://localhost:18000` (Production) | `http://localhost:8000` (Development)

**API Version:** v1

**Documentation URL:** `{BASE_URL}/docs` (Interactive Swagger UI)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [RFQ Management](#rfq-management)
4. [Supplier Management](#supplier-management)
5. [User Management](#user-management)
6. [AI Agent Services](#ai-agent-services)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Webhooks](#webhooks)
10. [SDKs and Integration Examples](#sdks-and-integration-examples)

---

## Authentication

### JWT Token-Based Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header for all protected endpoints.

#### Login Endpoint

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@company.com",
    "role": "buyer",
    "company_id": "uuid"
  }
}
```

#### Authentication Header Format

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### User Roles

- **buyer**: Can create RFQs, view suppliers, manage orders
- **supplier**: Can respond to RFQs, manage product catalog
- **admin**: Full system access
- **manager**: Company-level management access

---

## Core Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_agents": "active"
  }
}
```

### System Status

```http
GET /status
Authorization: Bearer {token}
```

**Response:**
```json
{
  "system_status": "operational",
  "uptime": "72:15:30",
  "active_users": 245,
  "active_rfqs": 12,
  "processed_today": 89
}
```

---

## RFQ Management

### Create RFQ

```http
POST /rfqs
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Concrete Admixtures for Dubai Project",
  "description": "High-performance PCE superplasticizers needed",
  "category": "chemicals",
  "quantity": 5000,
  "unit": "kg",
  "budget_min": 15000,
  "budget_max": 25000,
  "currency": "USD",
  "delivery_location": "Dubai, UAE",
  "delivery_deadline": "2024-02-15T00:00:00Z",
  "technical_specifications": {
    "type": "PCE Superplasticizer",
    "water_reduction": "30%",
    "slump_retention": "90 minutes",
    "chloride_content": "< 0.1%"
  },
  "documents": [
    {
      "name": "Technical Specification.pdf",
      "url": "https://storage.com/file123"
    }
  ]
}
```

**Response:**
```json
{
  "id": "rfq_uuid",
  "title": "Concrete Admixtures for Dubai Project",
  "status": "published",
  "rfq_number": "RFQ-2024-001",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-02-15T00:00:00Z",
  "estimated_suppliers": 15,
  "ai_analysis": {
    "market_insights": "High demand for PCE in UAE market",
    "price_prediction": "$4.2-4.8 per kg",
    "recommended_suppliers": ["BASF Turkey", "Sika Turkey"]
  }
}
```

### Get RFQ Details

```http
GET /rfqs/{rfq_id}
Authorization: Bearer {token}
```

### Update RFQ

```http
PUT /rfqs/{rfq_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated RFQ Title",
  "description": "Updated description",
  "status": "draft"
}
```

### List RFQs

```http
GET /rfqs?status=active&category=chemicals&page=1&limit=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: `draft`, `published`, `closed`, `awarded`
- `category`: Product category filter
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `search`: Search term

### Delete RFQ

```http
DELETE /rfqs/{rfq_id}
Authorization: Bearer {token}
```

---

## Supplier Management

### Discover Suppliers

```http
POST /suppliers/discover
Authorization: Bearer {token}
Content-Type: application/json

{
  "category": "chemicals",
  "location": "Turkey",
  "budget_range": {
    "min": 15000,
    "max": 25000
  },
  "requirements": {
    "certifications": ["ISO 9001", "CE"],
    "dubai_experience": true,
    "technical_support": true
  }
}
```

**Response:**
```json
{
  "total_found": 12,
  "suppliers": [
    {
      "id": "supplier_uuid",
      "company_name": "BASF Turkey",
      "contact_person": "Mehmet Demir",
      "email": "export.turkey@basf.com",
      "phone": "+90 216 349 2000",
      "location": "Istanbul, Turkey",
      "rating": 9.7,
      "certifications": ["ISO 9001:2015", "ISO 14001:2015"],
      "products": [
        {
          "name": "MasterGlenium 7700",
          "price_range": "$4.50-5.00",
          "moq": "1000 kg"
        }
      ],
      "delivery_time": "15-20 days",
      "dubai_projects": ["Dubai International Airport"]
    }
  ],
  "market_analysis": {
    "average_price": "$4.35/kg",
    "delivery_time_range": "12-25 days",
    "top_certifications": ["ISO 9001", "CE", "TSE"]
  }
}
```

### Get Supplier Details

```http
GET /suppliers/{supplier_id}
Authorization: Bearer {token}
```

### Supplier Catalog

```http
GET /suppliers/{supplier_id}/catalog
Authorization: Bearer {token}
```

---

## User Management

### Register User

```http
POST /users/register
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "role": "buyer",
  "company": {
    "name": "Construction Co Ltd",
    "country": "UAE",
    "industry": "Construction"
  }
}
```

### Get User Profile

```http
GET /users/me
Authorization: Bearer {token}
```

### Update User Profile

```http
PUT /users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+971 50 123 4567",
  "company_details": {
    "trade_license": "TL123456",
    "vat_number": "VAT987654"
  }
}
```

---

## AI Agent Services

### Get AI Market Insights

```http
POST /ai/market-insights
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_category": "chemicals",
  "region": "Middle East",
  "time_horizon": "3_months"
}
```

**Response:**
```json
{
  "insights": {
    "market_trend": "increasing",
    "price_forecast": {
      "direction": "stable",
      "expected_change": "±5%"
    },
    "supply_chain_status": "normal",
    "recommended_timing": "favorable",
    "key_factors": [
      "Strong construction growth in UAE",
      "Stable raw material prices",
      "Increasing quality requirements"
    ]
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### AI RFQ Analysis

```http
POST /ai/analyze-rfq
Authorization: Bearer {token}
Content-Type: application/json

{
  "rfq_id": "rfq_uuid"
}
```

### AI Supplier Recommendations

```http
POST /ai/recommend-suppliers
Authorization: Bearer {token}
Content-Type: application/json

{
  "rfq_requirements": {
    "category": "chemicals",
    "quantity": 5000,
    "budget": 20000,
    "location": "Dubai"
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "quantity",
      "issue": "Must be greater than 0"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_REQUIRED`: Valid token required
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `EXTERNAL_SERVICE_ERROR`: Third-party service unavailable

---

## Rate Limiting

### Rate Limits

- **Authenticated users**: 1000 requests/hour
- **Premium accounts**: 5000 requests/hour
- **AI endpoints**: 100 requests/hour
- **File uploads**: 50 requests/hour

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## Webhooks

### Webhook Events

Configure webhook endpoints to receive real-time notifications:

- `rfq.created`: New RFQ published
- `rfq.updated`: RFQ status changed
- `quote.received`: New supplier quote
- `order.placed`: Order confirmed
- `payment.completed`: Payment processed

### Webhook Payload Example

```json
{
  "event": "rfq.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "rfq_id": "rfq_uuid",
    "title": "Concrete Admixtures for Dubai Project",
    "status": "published",
    "buyer_id": "user_uuid"
  }
}
```

### Configure Webhooks

```http
POST /webhooks
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["rfq.created", "quote.received"],
  "secret": "webhook_secret_key"
}
```

---

## SDKs and Integration Examples

### JavaScript/Node.js SDK

```bash
npm install @agentik/b2b-sdk
```

```javascript
import { AgentikClient } from '@agentik/b2b-sdk';

const client = new AgentikClient({
  baseUrl: 'http://localhost:18000',
  apiKey: 'your_api_key'
});

// Create RFQ
const rfq = await client.rfqs.create({
  title: 'Steel Procurement',
  category: 'metals',
  quantity: 1000,
  unit: 'tons'
});

// Get suppliers
const suppliers = await client.suppliers.discover({
  category: 'metals',
  location: 'Turkey'
});
```

### Python SDK

```bash
pip install agentik-b2b-sdk
```

```python
from agentik import AgentikClient

client = AgentikClient(
    base_url="http://localhost:18000",
    api_key="your_api_key"
)

# Create RFQ
rfq = client.rfqs.create(
    title="Steel Procurement",
    category="metals",
    quantity=1000,
    unit="tons"
)

# Discover suppliers
suppliers = client.suppliers.discover(
    category="metals",
    location="Turkey"
)
```

### cURL Examples

#### Create RFQ with cURL

```bash
curl -X POST "http://localhost:18000/rfqs" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Concrete Admixtures",
    "category": "chemicals",
    "quantity": 5000,
    "unit": "kg",
    "budget_max": 25000
  }'
```

#### Get Market Insights

```bash
curl -X POST "http://localhost:18000/ai/market-insights" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "product_category": "chemicals",
    "region": "Middle East"
  }'
```

---

## Testing and Development

### Sandbox Environment

**Base URL:** `http://localhost:8000`

Test with sample data without affecting production.

### Postman Collection

Download our Postman collection: [B2B Agentik API Collection](./postman/B2B_Agentik_API.json)

### OpenAPI Specification

Full OpenAPI/Swagger specification available at: `{BASE_URL}/openapi.json`

---

## Support and Resources

### Documentation
- [User Manual](./USER_MANUAL.md)
- [System Architecture](./SYSTEM_ARCHITECTURE.md)
- [Development Roadmap](./B2B_AGENTIK_DEVELOPMENT_ROADMAP.md)

### Support Channels
- **Technical Support**: dev@agentik.com
- **Business Inquiries**: business@agentik.com
- **Documentation Issues**: docs@agentik.com

### Community
- [GitHub Repository](https://github.com/elkekoitan/B2B.git)
- [Developer Forum](https://forum.agentik.com)
- [Discord Community](https://discord.gg/agentik)

---

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- JWT authentication
- RFQ management endpoints
- Supplier discovery
- AI market insights
- Real-time webhooks

### Upcoming Features
- GraphQL API
- Advanced filtering
- Bulk operations
- Enhanced AI capabilities
- Mobile SDK support

---

*Last Updated: January 2024*
*API Version: 1.0.0*