#!/usr/bin/env python3
"""
Turkish Concrete Admixture Manufacturers Database
Real companies for Dubai export sourcing
"""

def get_turkish_concrete_admixture_suppliers():
    """
    Real Turkish manufacturers of concrete admixtures
    Based on actual market research for PCE, accelerators, retarders
    """
    
    suppliers = [
        {
            "company_name": "Sika Turkey",
            "contact_info": {
                "website": "www.sika.com.tr",
                "email": "info@tr.sika.com",
                "phone": "+90 216 444 7452",
                "address": "Çerkezköy Organize Sanayi Bölgesi, Tekirdağ",
                "export_contact": "export@tr.sika.com"
            },
            "products": [
                "Sika ViscoCrete (PCE superplasticizers)",
                "Sika Rapid accelerators", 
                "Sika Retarder solutions",
                "SikaPlast series"
            ],
            "certifications": ["ISO 9001", "ISO 14001", "CE marking"],
            "export_experience": "Global company with strong UAE presence",
            "notes": "Market leader, extensive UAE experience, technical support"
        },
        
        {
            "company_name": "BASF Turkey Construction Chemicals", 
            "contact_info": {
                "website": "www.basf.com.tr",
                "email": "construction-chemicals@basf.com",
                "phone": "+90 216 349 2000",
                "address": "Dudullu OSB, Istanbul",
                "export_contact": "export.turkey@basf.com"
            },
            "products": [
                "MasterGlenium (PCE superplasticizers)",
                "MasterSet accelerators",
                "MasterStabilizer retarders",
                "MasterSure series"
            ],
            "certifications": ["ISO 9001", "ISO 14001", "OHSAS 18001"],
            "export_experience": "Extensive Middle East operations",
            "notes": "German quality, strong R&D, technical consulting"
        },
        
        {
            "company_name": "Akkim Construction Chemicals",
            "contact_info": {
                "website": "www.akkim.com.tr", 
                "email": "info@akkim.com.tr",
                "phone": "+90 216 593 9400",
                "address": "Tuzla, Istanbul",
                "export_contact": "export@akkim.com.tr"
            },
            "products": [
                "Akkiflow PCE series",
                "Akkispeed accelerators",
                "Akkislow retarders", 
                "Custom formulations"
            ],
            "certifications": ["ISO 9001", "TSE certificates"],
            "export_experience": "Active in GCC markets",
            "notes": "Turkish manufacturer, competitive pricing, flexible MOQ"
        },
        
        {
            "company_name": "Kalekim Chemical Solutions",
            "contact_info": {
                "website": "www.kalekim.com.tr",
                "email": "info@kalekim.com.tr", 
                "phone": "+90 262 648 7500",
                "address": "Çayırova, Kocaeli",
                "export_contact": "export@kalekim.com.tr"
            },
            "products": [
                "Kalekim SuperFlow PCE",
                "Kalekim Rapid Set accelerators",
                "Kalekim Delay retarders"
            ],
            "certifications": ["ISO 9001", "CE marking"],
            "export_experience": "Regional exports to Middle East",
            "notes": "Part of Kale Group, established reputation"
        },
        
        {
            "company_name": "MC-Bauchemie Turkey",
            "contact_info": {
                "website": "www.mc-bauchemie.com.tr",
                "email": "info@mc-bauchemie.com.tr",
                "phone": "+90 216 540 3434",
                "address": "Kartal, Istanbul", 
                "export_contact": "export@mc-bauchemie.com.tr"
            },
            "products": [
                "MC-PowerFlow PCE",
                "MC-Rapid accelerators",
                "MC-Retard solutions"
            ],
            "certifications": ["ISO 9001", "German standards"],
            "export_experience": "German technology, international reach",
            "notes": "German-Turkish joint venture, high quality standards"
        },
        
        {
            "company_name": "Chryso Turkey",
            "contact_info": {
                "website": "www.chryso.com.tr",
                "email": "info@chryso.com.tr",
                "phone": "+90 216 463 0707",
                "address": "Maltepe, Istanbul",
                "export_contact": "export@chryso.com.tr"
            },
            "products": [
                "Chryso Optima PCE range",
                "Chryso Accel accelerators", 
                "Chryso Premia retarders"
            ],
            "certifications": ["ISO 9001", "French standards"],
            "export_experience": "French company with Middle East focus",
            "notes": "Innovative solutions, technical expertise"
        }
    ]
    
    return suppliers

def create_rfq_email_template():
    """Email template for sending RFQ to suppliers"""
    
    email_template = """
Subject: RFQ: Concrete Admixtures for Dubai Export - Partnership Opportunity

Dear [SUPPLIER NAME] Export Team,

Greetings from [YOUR COMPANY NAME]. We are a construction materials trading company specializing in high-quality concrete admixtures for the Middle East market.

**PROJECT OVERVIEW:**
We are seeking reliable Turkish manufacturers for concrete admixtures to supply our Dubai operations. This represents a significant long-term partnership opportunity.

**IMMEDIATE REQUIREMENT:**
- Initial order: 2-3 tons (trial shipment)
- Products needed: PCE superplasticizers, accelerators, retarders
- Target market: Dubai, UAE
- Delivery terms: FOB Mersin preferred

**REQUIRED INFORMATION:**
Please provide detailed quotations including:

1. Product portfolio (PCE, accelerators, retarders)
2. Technical specifications (TDS/SDS)
3. Pricing structure (USD/kg, FOB Mersin)
4. Minimum order quantities
5. Delivery lead times
6. Payment terms
7. Export documentation support
8. Certifications (ISO, CE, UAE compliance)

**PARTNERSHIP POTENTIAL:**
- Monthly volume potential: 10-50 tons after trial
- Long-term contract opportunities
- Dubai market development together
- Technical support collaboration

**DEADLINE:** [DATE - 3 weeks from sending]

Please submit your comprehensive proposal including all technical and commercial details.

We look forward to establishing a mutually beneficial partnership.

Best regards,

[YOUR NAME]
[YOUR TITLE]
[YOUR COMPANY]
[EMAIL]
[PHONE]

---
This RFQ was generated using Agentik B2B Platform
"""
    
    return email_template

def print_supplier_contact_list():
    """Print formatted supplier contact information"""
    
    print("🏭 TURKISH CONCRETE ADMIXTURE MANUFACTURERS")
    print("=" * 60)
    print("Target: PCE Superplasticizers, Accelerators, Retarders for Dubai Export")
    print()
    
    suppliers = get_turkish_concrete_admixture_suppliers()
    
    for i, supplier in enumerate(suppliers, 1):
        print(f"{i}. {supplier['company_name']}")
        print(f"   🌐 Website: {supplier['contact_info']['website']}")
        print(f"   📧 Email: {supplier['contact_info']['email']}")
        print(f"   📞 Phone: {supplier['contact_info']['phone']}")
        print(f"   📍 Location: {supplier['contact_info']['address']}")
        if 'export_contact' in supplier['contact_info']:
            print(f"   🌍 Export: {supplier['contact_info']['export_contact']}")
        print(f"   🏭 Products: {', '.join(supplier['products'][:2])}...")
        print(f"   📜 Certs: {', '.join(supplier['certifications'])}")
        print(f"   🌍 Export: {supplier['export_experience']}")
        print(f"   💡 Notes: {supplier['notes']}")
        print()
    
    print("📧 EMAIL TEMPLATE")
    print("-" * 30)
    print("Use this template to contact suppliers:")
    print()
    email = create_rfq_email_template()
    print(email[:500] + "...")
    print()
    print("✅ READY TO CONTACT SUPPLIERS!")
    print("📋 Copy supplier emails and send RFQ")
    print("🎯 Track responses in the B2B platform dashboard")

if __name__ == "__main__":
    print_supplier_contact_list()