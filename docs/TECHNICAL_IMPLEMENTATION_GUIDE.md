# 🛠️ B2B AGENTİK - TECHNICAL IMPLEMENTATION GUIDE

## 📋 Phase 1 Implementation Details

### 1.1 Enhanced Authentication & User Management

#### Technical Architecture
```typescript
// Role-based authentication system
interface UserRole {
  id: string;
  name: 'buyer' | 'supplier' | 'admin' | 'manager';
  permissions: Permission[];
}

interface Permission {
  resource: string;
  actions: ('create' | 'read' | 'update' | 'delete')[];
}
```

#### Implementation Steps

**Step 1: Database Schema Updates**
```sql
-- Add roles table
CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  permissions JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add user_role_assignments table
CREATE TABLE user_role_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  role_id UUID REFERENCES user_roles(id),
  assigned_by UUID REFERENCES auth.users(id),
  assigned_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add company verification table
CREATE TABLE company_verifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  document_type VARCHAR(50),
  document_url TEXT,
  verification_status VARCHAR(20) DEFAULT 'pending',
  verified_by UUID REFERENCES auth.users(id),
  verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Step 2: Backend API Implementation**
```python
# app/models/auth.py
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class UserRole(str, Enum):
    BUYER = "buyer"
    SUPPLIER = "supplier"
    ADMIN = "admin"
    MANAGER = "manager"

class Permission(BaseModel):
    resource: str
    actions: List[str]

class UserRoleModel(BaseModel):
    id: str
    name: UserRole
    permissions: List[Permission]

# app/auth/role_manager.py
class RoleManager:
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    async def assign_role(self, user_id: str, role_id: str, assigned_by: str):
        return self.db.table("user_role_assignments").insert({
            "user_id": user_id,
            "role_id": role_id,
            "assigned_by": assigned_by
        }).execute()
    
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        # Implementation for permission checking
        pass
```

**Step 3: Frontend Role-Based Components**
```typescript
// src/hooks/useAuth.ts
export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [roles, setRoles] = useState<UserRole[]>([]);
  
  const hasPermission = (resource: string, action: string): boolean => {
    return roles.some(role => 
      role.permissions.some(permission => 
        permission.resource === resource && 
        permission.actions.includes(action)
      )
    );
  };
  
  return { user, roles, hasPermission };
};

// src/components/RoleBasedRoute.tsx
export const RoleBasedRoute: React.FC<{
  allowedRoles: UserRole[];
  children: React.ReactNode;
}> = ({ allowedRoles, children }) => {
  const { roles } = useAuth();
  
  const hasAccess = roles.some(role => allowedRoles.includes(role.name));
  
  if (!hasAccess) {
    return <AccessDenied />;
  }
  
  return <>{children}</>;
};
```

### 1.2 Advanced RFQ Management System

#### Template Engine Implementation
```python
# app/services/rfq_template_service.py
from jinja2 import Environment, BaseLoader
from typing import Dict, Any

class RFQTemplateService:
    def __init__(self):
        self.templates = {
            "chemicals": {
                "fields": [
                    {"name": "chemical_name", "type": "text", "required": True},
                    {"name": "cas_number", "type": "text", "required": False},
                    {"name": "purity_level", "type": "select", "options": ["95%", "98%", "99%"]},
                    {"name": "packaging_type", "type": "select", "options": ["25kg bags", "50kg bags", "1000kg bags"]},
                    {"name": "storage_conditions", "type": "textarea", "required": True},
                    {"name": "safety_requirements", "type": "checkbox_list", "options": ["MSDS", "CoA", "Transportation permit"]}
                ],
                "compliance_checklist": [
                    "Chemical registration certificate",
                    "Export license for chemicals",
                    "Safety data sheet (SDS)",
                    "Certificate of analysis (CoA)"
                ]
            },
            "electronics": {
                "fields": [
                    {"name": "product_category", "type": "select", "options": ["Components", "Devices", "Systems"]},
                    {"name": "specifications", "type": "textarea", "required": True},
                    {"name": "certifications", "type": "checkbox_list", "options": ["CE", "FCC", "RoHS", "UL"]},
                    {"name": "warranty_period", "type": "select", "options": ["6 months", "1 year", "2 years"]},
                    {"name": "testing_requirements", "type": "textarea"}
                ],
                "compliance_checklist": [
                    "CE marking certificate",
                    "RoHS compliance certificate",
                    "Product testing reports",
                    "Export license if applicable"
                ]
            }
        }
    
    def get_template(self, category: str) -> Dict[str, Any]:
        return self.templates.get(category, self.templates["general"])
    
    def generate_rfq_form(self, category: str) -> Dict[str, Any]:
        template = self.get_template(category)
        return {
            "fields": template["fields"],
            "compliance_checklist": template["compliance_checklist"],
            "category": category
        }
```

#### Multi-Currency Implementation
```python
# app/services/currency_service.py
import aiohttp
from typing import Dict
from decimal import Decimal

class CurrencyService:
    def __init__(self):
        self.api_key = "your_exchange_rate_api_key"
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.supported_currencies = ["USD", "EUR", "TRY", "GBP"]
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Decimal]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{base_currency}") as response:
                data = await response.json()
                return {
                    currency: Decimal(str(rate))
                    for currency, rate in data["rates"].items()
                    if currency in self.supported_currencies
                }
    
    async def convert_currency(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return amount
        
        rates = await self.get_exchange_rates(from_currency)
        return amount * rates[to_currency]

# app/models/rfq.py (updated)
class RFQCreate(BaseModel):
    # ... existing fields ...
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    currency: str = "USD"  # New field
    
class RFQ(BaseModel):
    # ... existing fields ...
    budget_min_usd: Optional[Decimal] = None  # Converted to USD for comparison
    budget_max_usd: Optional[Decimal] = None
    original_currency: str = "USD"
```

#### Frontend Currency Component
```typescript
// src/components/CurrencySelector.tsx
export const CurrencySelector: React.FC<{
  value: string;
  onChange: (currency: string) => void;
}> = ({ value, onChange }) => {
  const currencies = [
    { code: "USD", symbol: "$", name: "US Dollar" },
    { code: "EUR", symbol: "€", name: "Euro" },
    { code: "TRY", symbol: "₺", name: "Turkish Lira" },
    { code: "GBP", symbol: "£", name: "British Pound" }
  ];
  
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {currencies.map(currency => (
          <SelectItem key={currency.code} value={currency.code}>
            {currency.symbol} {currency.name} ({currency.code})
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

// src/hooks/useCurrency.ts
export const useCurrency = () => {
  const [rates, setRates] = useState<Record<string, number>>({});
  
  const convertCurrency = (amount: number, from: string, to: string): number => {
    if (from === to) return amount;
    if (!rates[from] || !rates[to]) return amount;
    
    // Convert to USD first, then to target currency
    const usdAmount = amount / rates[from];
    return usdAmount * rates[to];
  };
  
  const formatCurrency = (amount: number, currency: string): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };
  
  return { rates, convertCurrency, formatCurrency };
};
```

### 1.3 Supplier Portal Development

#### Supplier Dashboard Backend
```python
# app/models/supplier.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SupplierProfile(BaseModel):
    id: str
    company_name: str
    contact_person: str
    email: str
    phone: str
    website: Optional[str]
    address: str
    business_license: str
    tax_number: str
    establishment_year: int
    employee_count: int
    annual_revenue: Optional[Decimal]
    export_experience_years: int
    certifications: List[str]
    primary_markets: List[str]
    product_categories: List[str]
    languages_spoken: List[str]
    verified: bool = False
    verification_score: int = 0
    created_at: datetime
    updated_at: datetime

class SupplierCatalog(BaseModel):
    id: str
    supplier_id: str
    product_name: str
    product_code: str
    category: str
    description: str
    specifications: Dict[str, Any]
    price: Decimal
    currency: str
    moq: int
    unit: str
    lead_time_days: int
    certifications: List[str]
    images: List[str]
    documents: List[str]
    active: bool = True

# app/api/routes/supplier.py
@router.post("/profile", response_model=BaseResponse)
async def update_supplier_profile(
    profile: SupplierProfile,
    current_user: dict = Depends(get_current_user)
):
    # Update supplier profile
    pass

@router.post("/catalog/products", response_model=BaseResponse)
async def add_catalog_product(
    product: SupplierCatalog,
    current_user: dict = Depends(get_current_user)
):
    # Add product to supplier catalog
    pass

@router.get("/dashboard/analytics", response_model=BaseResponse)
async def get_supplier_analytics(
    current_user: dict = Depends(get_current_user)
):
    # Return supplier performance analytics
    pass
```

#### Supplier Dashboard Frontend
```typescript
// src/pages/supplier/SupplierDashboard.tsx
export const SupplierDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<SupplierAnalytics | null>(null);
  const [activeRFQs, setActiveRFQs] = useState<RFQ[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  return (
    <div className="supplier-dashboard">
      <div className="dashboard-header">
        <h1>Supplier Dashboard</h1>
        <div className="quick-stats">
          <StatCard title="Active RFQs" value={analytics?.activeRFQs || 0} />
          <StatCard title="Response Rate" value={`${analytics?.responseRate || 0}%`} />
          <StatCard title="Average Score" value={analytics?.averageScore || 0} />
          <StatCard title="This Month Revenue" value={analytics?.monthlyRevenue || 0} />
        </div>
      </div>
      
      <div className="dashboard-content">
        <div className="left-panel">
          <RFQNotifications rfqs={activeRFQs} />
          <PerformanceChart data={analytics?.performanceData} />
        </div>
        
        <div className="right-panel">
          <QuickActions />
          <RecentActivity activities={analytics?.recentActivities} />
        </div>
      </div>
    </div>
  );
};

// src/components/supplier/RFQNotifications.tsx
export const RFQNotifications: React.FC<{ rfqs: RFQ[] }> = ({ rfqs }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>New RFQ Opportunities</CardTitle>
      </CardHeader>
      <CardContent>
        {rfqs.map(rfq => (
          <div key={rfq.id} className="rfq-notification">
            <div className="rfq-header">
              <h4>{rfq.title}</h4>
              <Badge variant={getRFQUrgency(rfq.deadline)}>
                {formatDeadline(rfq.deadline)}
              </Badge>
            </div>
            <p className="rfq-description">{rfq.description}</p>
            <div className="rfq-actions">
              <Button variant="outline" size="sm">View Details</Button>
              <Button size="sm">Submit Quote</Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
```

## 🧪 Testing Strategy

### Unit Testing
```python
# tests/test_rfq_service.py
import pytest
from app.services.rfq_service import RFQService
from app.models.rfq import RFQCreate

@pytest.fixture
def rfq_service():
    return RFQService()

@pytest.fixture
def sample_rfq():
    return RFQCreate(
        title="Test RFQ",
        category="chemicals",
        description="Test description",
        quantity=100,
        unit="kg",
        budget_min=1000,
        budget_max=2000,
        currency="USD",
        deadline=datetime.now() + timedelta(days=30)
    )

class TestRFQService:
    async def test_create_rfq(self, rfq_service, sample_rfq):
        result = await rfq_service.create_rfq(sample_rfq, user_id="test-user")
        assert result["success"] is True
        assert "rfq" in result["data"]
    
    async def test_get_template(self, rfq_service):
        template = rfq_service.get_template("chemicals")
        assert "fields" in template
        assert "compliance_checklist" in template
    
    async def test_currency_conversion(self, rfq_service):
        converted = await rfq_service.convert_currency(100, "USD", "EUR")
        assert converted > 0
        assert converted != 100  # Should be different unless rates are 1:1
```

### Integration Testing
```python
# tests/test_api_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_rfq_creation_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpass"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create RFQ
        rfq_response = await client.post("/rfqs", json={
            "title": "Integration Test RFQ",
            "category": "chemicals",
            "description": "Test description",
            "quantity": 100,
            "unit": "kg"
        }, headers={"Authorization": f"Bearer {token}"})
        
        assert rfq_response.status_code == 200
        assert rfq_response.json()["success"] is True
```

### Frontend Testing
```typescript
// src/components/__tests__/RFQForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RFQForm } from '../RFQForm';

describe('RFQForm', () => {
  test('renders form fields correctly', () => {
    render(<RFQForm />);
    
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
  });
  
  test('validates required fields', async () => {
    render(<RFQForm />);
    
    const submitButton = screen.getByText(/submit/i);
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });
  });
  
  test('submits form with valid data', async () => {
    const mockOnSubmit = jest.fn();
    render(<RFQForm onSubmit={mockOnSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test RFQ' }
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: 'chemicals' }
    });
    
    fireEvent.click(screen.getByText(/submit/i));
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Test RFQ',
        category: 'chemicals'
      }));
    });
  });
});
```

## 🚀 Deployment Strategy
### Repository Structure & Commands
```
agentik-b2b-app/backend/app   # FastAPI backend
frontend/                     # React + Vite web
agent_orchestrator/           # Agents service
```
Common dev commands:
```
docker compose build && docker compose up -d
docker compose logs -f backend
```

### RBAC Enforcement in Endpoints
```python
from app.core.permissions import require_permission

@router.post("/", dependencies=[Depends(require_permission("rfq:create"))])
async def create_rfq(...):
    ...
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: pytest
      
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker images
        run: |
          docker build -t agentik-backend .
          docker build -t agentik-frontend ./frontend
          
      - name: Deploy to production
        run: |
          # Deploy using your preferred method (Docker Swarm, Kubernetes, etc.)
          docker-compose -f docker-compose.prod.yml up -d
```

### Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: agentik-backend:latest
    environment:
      - ENVIRONMENT=production
      - SUPABASE_URL=${SUPABASE_URL}
      - REDIS_URL=redis://redis:6379
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
  
  frontend:
    image: agentik-frontend:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl
    deploy:
      replicas: 2
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 512M
```

This technical implementation guide provides the detailed code structure and implementation approach for Phase 1 of the roadmap. Each subsequent phase will have similar detailed technical specifications.
