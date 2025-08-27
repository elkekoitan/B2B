# B2B Agentik Platform - Figma Design Specifications

## Overview

Complete design system and screen specifications for implementing the B2B Agentik platform in Figma.

**Design Version:** 1.0.0  
**Target Platforms:** Web Desktop, Tablet, Mobile  

---

## Design System Foundation

### Color Palette

```css
/* Primary Colors */
--primary-blue: #2563EB;
--primary-blue-light: #3B82F6;
--primary-blue-dark: #1E40AF;

/* Secondary Colors */
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;

/* Grays */
--gray-50: #F8FAFC;
--gray-100: #F1F5F9;
--gray-200: #E2E8F0;
--gray-500: #64748B;
--gray-900: #0F172A;
```

### Typography

```css
/* Font: Inter */
H1: 48px, Bold (700)
H2: 36px, Semibold (600)
H3: 24px, Semibold (600)
H4: 20px, Semibold (600)
Body Large: 18px, Regular (400)
Body: 16px, Regular (400)
Body Small: 14px, Regular (400)
Caption: 12px, Regular (400)
```

### Spacing System

```css
4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px, 80px, 96px
```

---

## Key Components

### Buttons

#### Primary Button
- Background: `--primary-blue`
- Text: White, 16px, Medium (500)
- Padding: 12px 24px
- Border-radius: 8px
- Hover: Lift effect + darker background

#### Secondary Button  
- Background: Transparent
- Border: 1px solid `--primary-blue`
- Text: `--primary-blue`, 16px, Medium (500)
- Hover: Fill with primary color

### Form Elements

#### Input Field
- Height: 44px
- Padding: 12px 16px
- Border: 1px solid `--gray-200`
- Border-radius: 8px
- Focus: Border `--primary-blue` + shadow

### Cards

#### RFQ Card
- Background: White
- Border-radius: 12px
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Border-left: 4px solid `--primary-blue`
- Padding: 20px

#### Supplier Card
- Background: White
- Border-radius: 12px
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Hover: Lift effect
- Padding: 24px

---

## Screen Designs

### 1. Authentication Screens

#### Login Screen
```
Layout: Centered card (400px max-width)
Components:
- Logo (top center)
- Email input field
- Password input field
- "Remember me" checkbox
- Primary button "Sign In"
- Social login buttons (Google, LinkedIn)
- "Forgot Password?" link
- "Sign up" link
```

#### Registration Screen
```
Layout: Centered with account type selection
Components:
- Account type cards (Buyer/Supplier)
- Registration form (email, password, company)
- Terms checkbox
- Primary button "Create Account"
```

### 2. Dashboard Screens

#### Buyer Dashboard
```
Layout: Sidebar + Main content
Sidebar (280px):
- Navigation items with icons
- Dashboard, Create RFQ, My RFQs, Suppliers, Orders, Analytics, Settings

Main Content:
- Welcome header with user name
- KPI cards (3 columns): Active RFQs, Received Quotes, Orders
- Recent RFQs list with status badges
- AI insights widget
- Quick action buttons
```

#### Supplier Dashboard
```
Layout: Similar to buyer with different content
Sidebar:
- Dashboard, RFQ Marketplace, My Quotes, Orders, Catalog, Performance

Main Content:
- KPI cards: New RFQs, Active Quotes, Won Orders
- New RFQ opportunities list
- Performance analytics widget
```

### 3. RFQ Creation Wizard

#### 4-Step Process
```
Step 1 - Basic Info:
- RFQ title input
- Category dropdown
- Description textarea
- Progress indicator (●○○○)

Step 2 - Specifications:
- Quantity + Unit inputs
- Budget range (min/max)
- Technical specs builder
- Progress indicator (●●○○)

Step 3 - Delivery:
- Location input with map
- Deadline date picker
- Payment terms dropdown
- File upload area
- Progress indicator (●●●○)

Step 4 - Review:
- Summary card with all details
- Visibility settings (Public/Private)
- Final action buttons
- Progress indicator (●●●●)
```

### 4. Supplier Discovery

#### Search Interface
```
Layout: Filters + Results
Components:
- Smart search bar with AI icon
- Filter panel (Category, Location, Certifications)
- Supplier cards grid/list view
- Each card shows: Company name, rating, location, products, price range, certifications
- Action buttons: View Profile, Contact
```

#### Supplier Profile
```
Layout: Full page with tabs
Header:
- Company name and logo
- Rating and location
- Contact information
- Primary action buttons

Content Tabs:
- About (company description, capabilities)
- Products (catalog with prices)
- Certifications (with validity dates)
- Reviews (customer feedback)
- Projects (case studies)
```

### 5. Mobile Responsive

#### Mobile Dashboard
```
Layout: Stack vertically
Components:
- Hamburger menu header
- KPI cards (stacked, not side-by-side)
- Simplified navigation
- Quick action floating button
- Bottom tab navigation
```

#### Mobile RFQ Creation
```
Layout: Full-screen steps
- Single column form
- Larger touch targets (44px minimum)
- Simplified navigation
- Bottom action buttons
```

---

## Figma Implementation Guide

### Project Setup

#### 1. Create Figma Project
```
Project Name: B2B Agentik Platform
Structure:
├── 🎨 Design System
├── 🖥️ Desktop Screens  
├── 📱 Mobile Screens
└── 🔄 Prototypes
```

#### 2. Design System Setup

**Colors (Local Styles):**
```
Primary/Blue
Primary/Blue Light  
Primary/Blue Dark
Success/Green
Warning/Orange
Error/Red
Gray/50 through Gray/900
```

**Typography (Text Styles):**
```
Heading/H1
Heading/H2
Heading/H3
Heading/H4
Body/Large
Body/Base
Body/Small
Caption
```

**Components:**
```
Buttons/Primary
Buttons/Secondary
Forms/Input
Forms/Select
Cards/Base
Cards/RFQ
Cards/Supplier
Navigation/Header
Navigation/Sidebar
```

### 3. Screen Creation Process

#### Step 1: Create Master Components
1. Build button components with variants (Primary, Secondary, sizes)
2. Create form input components
3. Build card components for RFQs and suppliers
4. Design navigation components

#### Step 2: Design Key Screens
1. **Start with Login/Registration** (simplest)
2. **Create Dashboard layouts** (establish grid)
3. **Build RFQ creation flow** (complex workflow)
4. **Design supplier discovery** (search & filters)
5. **Create mobile versions** (responsive adaptations)

#### Step 3: Create Prototypes
1. **User Flow 1:** Buyer journey (Login → Dashboard → Create RFQ → Review Quotes)
2. **User Flow 2:** Supplier journey (Login → Dashboard → Browse RFQs → Submit Quote)
3. **Admin Flow:** Platform management and analytics

### 4. Implementation Guidelines

#### Design Tokens
```
Export design tokens for development:
- Colors (CSS custom properties)
- Typography (font-size, line-height, font-weight)
- Spacing (margin, padding values)
- Border-radius values
- Shadow definitions
```

#### Component Specifications
```
For each component, document:
- Default state
- Hover state
- Active/pressed state
- Disabled state
- Loading state (where applicable)
- Error state (for forms)
```

#### Responsive Breakpoints
```
Mobile: 320px - 767px
Tablet: 768px - 1023px
Desktop: 1024px+

Design for mobile-first, then scale up
```

---

## Key Screens Checklist

### Authentication ✅
- [ ] Login screen
- [ ] Registration (Buyer/Supplier)
- [ ] Password reset
- [ ] Email verification

### Buyer Screens ✅
- [ ] Dashboard
- [ ] Create RFQ (4-step wizard)
- [ ] RFQ management list
- [ ] Supplier discovery
- [ ] Supplier profiles
- [ ] Quote comparison
- [ ] Order management

### Supplier Screens ✅
- [ ] Dashboard
- [ ] RFQ marketplace
- [ ] Quote creation
- [ ] Order management  
- [ ] Catalog management
- [ ] Performance analytics

### Shared Screens ✅
- [ ] User profile settings
- [ ] Notifications center
- [ ] Help & support
- [ ] AI insights dashboard

### Mobile Versions ✅
- [ ] Mobile authentication
- [ ] Mobile dashboards
- [ ] Mobile RFQ creation
- [ ] Mobile supplier search

---

## Design Assets Needed

### Icons
```
Navigation: Dashboard, RFQ, Suppliers, Orders, Analytics, Settings
Actions: Create, Edit, Delete, Search, Filter, Upload
Status: Active, Pending, Completed, Cancelled
General: User, Notification, Menu, Close, Arrow, Check
```

### Illustrations
```
Empty states (No RFQs, No suppliers found)
Error states (404, 500, Network error)
Success confirmations (RFQ published, Quote submitted)
Onboarding (Welcome screens, Feature explanations)
```

### Sample Data
```
Company names: BASF Turkey, Sika Turkey, Akkim Construction
User names: Mehmet Demir, Fatma Yılmaz, Ahmed Hassan
Product examples: PCE Superplasticizers, Concrete Admixtures
Locations: Istanbul, Dubai, Ankara, Izmir
```

---

## Handoff to Development

### Export Guidelines
```
Images: 2x resolution for retina displays
Icons: SVG format with optimized paths
Components: Consistent naming convention
Specifications: Include padding, margins, colors, fonts
Interactive states: Document hover, active, disabled states
```

### CSS Output
```
Generate CSS for:
- Color variables
- Typography classes  
- Component styles
- Responsive breakpoints
- Animation/transition values
```

This specification provides everything needed to implement the complete B2B Agentik platform design in Figma, from design system setup to final screen designs and development handoff.

---

*Design System Version: 1.0.0*  
*Last Updated: January 2024*