# B2B Agentik Platform - Key Screen Wireframes

## Essential Screen Layouts for Figma Implementation

This document provides wireframes for the most important screens in the B2B Agentik platform.

---

## 1. Login Screen
```
┌─────────────────────────────────────┐
│           [B2B Agentik Logo]        │
│                                     │
│         ┌─────────────────┐         │
│         │   Welcome Back  │         │
│         │                 │         │
│         │ Email Address   │         │
│         │ [_____________] │         │
│         │                 │         │
│         │ Password        │         │
│         │ [_____________] │         │
│         │                 │         │
│         │ ☐ Remember me   │         │
│         │                 │         │
│         │   [  Sign In  ] │         │
│         │                 │         │
│         │ ──── OR ────    │         │
│         │                 │         │
│         │ [Google][LinkedIn]│        │
│         │                 │         │
│         │ Forgot password?│         │
│         │ Sign up         │         │
│         └─────────────────┘         │
└─────────────────────────────────────┘
```

---

## 2. Buyer Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ [≡] B2B Agentik              [🔔] [Search] [👤 Profile] │
├─────────┬───────────────────────────────────────────────┤
│   🏠    │            Welcome back, John!              │
│Dashboard│                                               │
│         │  ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│ 📝 RFQs │  │ Active  │ │Received │ │Complete │         │
│ Create  │  │  RFQs   │ │ Quotes  │ │ Orders  │         │
│ Manage  │  │   12    │ │   24    │ │    8    │         │
│         │  └─────────┘ └─────────┘ └─────────┘         │
│ 🔍      │                                               │
│Suppliers│                Recent RFQs                    │
│         │  ┌─────────────────────────────────────────┐ │
│ 📦      │  │ Concrete Admixtures for Dubai Project   │ │
│Orders   │  │ Status: ●Active    Expires: 5 days     │ │
│         │  │ 8 Responses       Budget: $20K-25K     │ │
│ 📊      │  │ [View Details] [Compare Quotes]        │ │
│Analytics│  └─────────────────────────────────────────┘ │
│         │                                               │
│ ⚙️      │           AI Market Insights                 │
│Settings │  ┌─────────────────────────────────────────┐ │
│         │  │ 📈 Chemical prices trending up 3%      │ │
│         │  │ 🎯 Best suppliers: BASF, Sika Turkey   │ │
│         │  │ [View Full Analysis]                   │ │
│         │  └─────────────────────────────────────────┘ │
└─────────┴───────────────────────────────────────────────┘
```

---

## 3. Create RFQ Wizard (Step 1)
```
┌─────────────────────────────────────┐
│          Create New RFQ             │
│                                     │
│  Step 1 of 4: Basic Information    │
│  ●○○○                              │
│                                     │
│  RFQ Title *                        │
│  ┌─────────────────────────────┐   │
│  │ Concrete Admixtures for...  │   │
│  └─────────────────────────────┘   │
│                                     │
│  Product Category *                 │
│  ┌─────────────────────────────┐   │
│  │ Chemicals                ▼ │   │
│  └─────────────────────────────┘   │
│                                     │
│  Description *                      │
│  ┌─────────────────────────────┐   │
│  │ High-performance PCE        │   │
│  │ superplasticizers needed    │   │
│  │ for Dubai construction...   │   │
│  └─────────────────────────────┘   │
│                                     │
│           [Cancel] [Next →]        │
└─────────────────────────────────────┘
```

---

## 4. Supplier Discovery
```
┌─────────────────────────────────────────────────────────┐
│                    Find Suppliers                      │
│                                                         │
│  🤖 Smart Search                                        │
│  ┌─────────────────────────────────────────────────┐🔍│
│  │ Chemical suppliers in Turkey for Dubai...        │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Filters: [Category▼] [Location▼] [Budget▼] [Apply]    │
│                                                         │
│  Results: 12 suppliers found                           │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🏢 BASF Turkey                            ⭐9.7 │   │
│  │ 📍 Istanbul    💰 $4.50-5.00/kg                │   │
│  │ PCE Superplasticizers, 25+ years experience    │   │
│  │ ✅ ISO 9001, CE  🚚 15-20 days to Dubai        │   │
│  │ 🎯 96% match for your requirements             │   │
│  │        [View Profile]  [Contact]  [Add to RFQ] │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🏢 Sika Turkey                            ⭐9.8 │   │
│  │ 📍 Tekirdağ    💰 $4.20-4.80/kg               │   │
│  │ Construction Chemicals, Premium quality        │   │
│  │ ✅ ISO 9001, ISO 14001  🚚 15-20 days         │   │
│  │ 🎯 94% match for your requirements             │   │
│  │        [View Profile]  [Contact]  [Add to RFQ] │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Supplier Profile
```
┌─────────────────────────────────────────────────────────┐
│ [← Back to Search]                                      │
│                                                         │
│  🏢 BASF Turkey                                ⭐ 9.7  │
│  📍 Istanbul  📞 +90 216 349 2000                      │
│  ✉️ export.turkey@basf.com                            │
│                                                         │
│     [💬 Contact Supplier]  [📄 Request Quote]          │
│                                                         │
│  ┌─ About Company ─────────────────────────────────┐   │
│  │ Leading chemical supplier, 25+ years export    │   │
│  │ experience. Direct UAE market access.          │   │
│  │ Monthly capacity: 800 tons.                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Product Catalog ───────────────────────────────┐   │
│  │ PCE Superplasticizers                          │   │
│  │ • MasterGlenium 7700: $4.85/kg, MOQ: 1000kg   │   │
│  │ • Latest generation PCE, 35% water reduction   │   │
│  │                                                 │   │
│  │ Accelerators                                   │   │
│  │ • MasterSet R 100: $3.95/kg, MOQ: 500kg       │   │
│  │ • Rapid strength, low chloride                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Certifications ────────────────────────────────┐   │
│  │ ✅ ISO 9001:2015  ✅ ISO 14001:2015            │   │
│  │ ✅ OHSAS 18001   ✅ UAE Standards               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Mobile Dashboard
```
┌─────────────────┐
│ [≡] B2B [🔔][👤]│
├─────────────────┤
│ Welcome Back!   │
│ John Doe        │
│                 │
│ ┌─────┬─────┬───┐│
│ │ 12  │ 24  │ 8 ││
│ │RFQs │Quote│Ord││
│ └─────┴─────┴───┘│
│                 │
│ Recent RFQs     │
│ ┌─────────────┐ │
│ │ Concrete    │ │
│ │ Admixtures  │ │
│ │ ●Active     │ │
│ │ 8 Responses │ │
│ │ [View][Edit]│ │
│ └─────────────┘ │
│                 │
│ [+ Create RFQ]  │
│                 │
│ Quick Actions   │
│ [Find Suppliers]│
│ [View Analytics]│
│ [Manage Orders] │
└─────────────────┘
```

---

## 7. Mobile RFQ Creation
```
┌─────────────────┐
│ ← Create RFQ    │
├─────────────────┤
│ Step 1 of 4     │
│ ●○○○           │
│                 │
│ RFQ Title*      │
│ ┌─────────────┐ │
│ │ Concrete... │ │
│ └─────────────┘ │
│                 │
│ Category*       │
│ ┌─────────────┐ │
│ │Chemicals ▼  │ │
│ └─────────────┘ │
│                 │
│ Description*    │
│ ┌─────────────┐ │
│ │ High-perf   │ │
│ │ PCE needed  │ │
│ │ for Dubai...│ │
│ └─────────────┘ │
│                 │
│   [Cancel][Next]│
└─────────────────┘
```

---

## 8. AI Market Insights
```
┌─────────────────────────────────────────────────────────┐
│  AI Market Intelligence Dashboard                       │
│                                                         │
│  ┌─ Price Trends ──────────────────────────────────┐   │
│  │ 📈 Chemical Prices                              │   │
│  │ Current: $4.35/kg ↑3% (vs last month)          │   │
│  │ Forecast: Stable next 3 months                  │   │
│  │ [View Detailed Chart]                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Supply Chain Status ───────────────────────────┐   │
│  │ 🟢 Normal Operations                            │   │
│  │ Turkey → UAE: 15-20 days average               │   │
│  │ No major disruptions expected                   │   │
│  │ [View Full Report]                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Supplier Recommendations ──────────────────────┐   │
│  │ 🤖 AI Suggests for your RFQ                    │   │
│  │                                                 │   │
│  │ 1. BASF Turkey (96% match)                     │   │
│  │    Premium quality, fast delivery              │   │
│  │                                                 │   │
│  │ 2. Sika Turkey (94% match)                     │   │
│  │    Cost-effective, reliable                    │   │
│  │                                                 │   │
│  │ 3. Akkim Construction (89% match)              │   │
│  │    Competitive pricing, good service           │   │
│  │                                                 │   │
│  │ [View All Suggestions]                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Figma Implementation Steps

### 1. Project Setup
```
Create Project: "B2B Agentik Platform"
File Structure:
├── 🎨 Design System (Colors, Typography, Components)
├── 🖥️ Desktop Screens (All web screens)
├── 📱 Mobile Screens (Responsive versions)
└── 🔄 Prototypes (User flows)
```

### 2. Design System First
```
Colors: Create local color styles for all brand colors
Typography: Set up text styles for all headings and body text
Components: Build master components for buttons, forms, cards
Icons: Create or import icon set for navigation and actions
```

### 3. Screen Priority Order
```
1. Login/Registration (Foundation)
2. Dashboard screens (Core experience)  
3. RFQ creation flow (Key functionality)
4. Supplier discovery (Important feature)
5. Mobile responsive versions
6. Prototype user flows
```

### 4. Component Library
```
Essential Components:
- Primary/Secondary buttons with hover states
- Form inputs with focus states
- RFQ cards with status indicators
- Supplier cards with rating displays
- Navigation sidebar with active states
- Header with user profile dropdown
- Mobile navigation with hamburger menu
```

### 5. Responsive Design
```
Breakpoints:
- Mobile: 320px - 767px
- Tablet: 768px - 1023px  
- Desktop: 1024px+

Mobile-first approach: Design mobile layouts first, then adapt for larger screens
```

This wireframe specification provides the essential screen layouts needed to implement the complete B2B Agentik platform design in Figma, with clear visual structure and component specifications.

---

*Wireframe Version: 1.0.0*  
*Last Updated: January 2024*