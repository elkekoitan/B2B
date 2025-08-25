#!/usr/bin/env python3
"""
Real RFQ: Concrete Admixtures for Dubai Export
This creates an actual business RFQ for concrete admixture suppliers
"""
import requests
import json
from datetime import datetime, timedelta

def create_real_concrete_admixture_rfq():
    print("🏗️ CREATING REAL RFQ: CONCRETE ADMIXTURES FOR DUBAI EXPORT")
    print("=" * 70)
    
    # Real RFQ data based on your requirements
    rfq_data = {
        'title': 'Beton Katkı Maddeleri Tedariki - Dubai İhracat Projesi',
        'description': '''Dubai'ye ihracat yapmak için güvenilir beton katkı maddesi tedarikçileri arıyoruz. 

Gerekli Ürünler:
• PCE Süperplastikleştiriciler
• Hızlandırıcılar (Accelerators)  
• Geciktiriciler (Retarders)

İlk aşamada 2-3 ton deneme siparişi planlanmaktadır. Uzun vadeli partnership potansiyeli mevcuttur.

Teknik Gereksinimler:
- Yüksek kalite standartları
- Dubai market standartlarına uygunluk
- Consistent quality assurance
- Technical support capability

İhracat Detayları:
- Hedef pazar: Dubai, UAE
- Tahmini aylık volüm: 10-50 ton (başlangıç sonrası)
- Packaging: Export standardında ambalaj
- Logistics: FOB Mersin port preferred''',
        
        'category': 'chemicals',
        'quantity': 3,  # 2-3 ton initial order
        'unit': 'tons',
        'budget_min': 8000,   # Realistic budget for 3 tons
        'budget_max': 15000,
        'deadline': (datetime.now() + timedelta(days=21)).isoformat() + 'Z',  # 3 weeks
        'delivery_location': 'FOB Mersin Port, Turkey → Dubai, UAE',
        'requirements': '''ZORUNLU BELGELER VE BİLGİLER:

1. ÜRÜN BİLGİLERİ:
   • Ürün türleri (PCE, Accelerator, Retarder)
   • Technical Data Sheets (TDS)
   • Safety Data Sheets (SDS)
   • Product specifications

2. FİYATLANDIRMA:
   • Fiyat/kg (EXW veya FOB Mersin)
   • Minimum sipariş miktarı (MOQ)
   • Volume discount structure
   • Payment terms

3. İHRACAT KAPASİTESİ:
   • Export experience to UAE/GCC
   • Monthly production capacity
   • Lead time for production
   • Packaging options for export

4. SERTİFİKALAR:
   • ISO 9001 Quality Management
   • ISO 14001 Environmental (preferred)
   • CE marking (if applicable)
   • UAE/Dubai market compliance certificates
   • Export licenses

5. TEKNİK DESTEK:
   • Technical support availability
   • Application guidance
   • Quality assurance procedures
   • After-sales support

6. LOJİSTİK:
   • Shipping arrangements capability
   • Documentation support (export docs)
   • Insurance and shipping terms
   • Container loading capacity'''
    }
    
    print("📋 RFQ DETAILS:")
    print(f"Title: {rfq_data['title']}")
    print(f"Category: {rfq_data['category']}")
    print(f"Initial Quantity: {rfq_data['quantity']} {rfq_data['unit']}")
    print(f"Budget Range: ${rfq_data['budget_min']:,} - ${rfq_data['budget_max']:,}")
    print(f"Deadline: {rfq_data['deadline'][:10]}")
    print(f"Delivery: {rfq_data['delivery_location']}")
    print()
    
    try:
        # Create the RFQ via API
        response = requests.post(
            'http://localhost:8000/rfqs',
            headers={
                'Authorization': 'Bearer mock-admin-token',
                'Content-Type': 'application/json'
            },
            json=rfq_data
        )
        
        if response.status_code == 200:
            data = response.json()
            rfq_id = data.get('data', {}).get('rfq', {}).get('id')
            
            print("✅ RFQ CREATED SUCCESSFULLY!")
            print(f"🆔 RFQ ID: {rfq_id}")
            print(f"📅 Created: {data.get('data', {}).get('rfq', {}).get('created_at', 'Unknown')}")
            print()
            
            # Show what suppliers should provide
            print("📊 SUPPLIER INFORMATION TEMPLATE")
            print("-" * 50)
            supplier_template = {
                "company_info": {
                    "company_name": "Example: ABC Chemicals Ltd.",
                    "contact_person": "Ahmet Yılmaz",
                    "email": "export@abcchemicals.com.tr",
                    "phone": "+90 232 XXX XXXX",
                    "address": "Izmir, Turkey",
                    "website": "www.abcchemicals.com.tr"
                },
                "products": {
                    "pce_superplasticizers": {
                        "product_name": "ABC-PCE-2024",
                        "price_per_kg": "4.50 USD/kg FOB Mersin",
                        "moq": "1 ton",
                        "technical_specs": "40% solid content, chloride-free"
                    },
                    "accelerators": {
                        "product_name": "ABC-ACC-Fast",
                        "price_per_kg": "3.20 USD/kg FOB Mersin", 
                        "moq": "500 kg",
                        "technical_specs": "Non-chloride accelerator"
                    },
                    "retarders": {
                        "product_name": "ABC-RET-Slow",
                        "price_per_kg": "2.80 USD/kg FOB Mersin",
                        "moq": "500 kg", 
                        "technical_specs": "Sugar-based retarder"
                    }
                },
                "certifications": [
                    "ISO 9001:2015",
                    "ISO 14001:2015", 
                    "CE Marking",
                    "TSE Certificate"
                ],
                "export_terms": {
                    "payment_terms": "30% advance, 70% against B/L copy",
                    "delivery_time": "15-20 days after order confirmation",
                    "packaging": "25kg bags, 1000kg big bags",
                    "container_capacity": "20 tons per 20ft container"
                }
            }
            
            print("Expected supplier response format:")
            print(json.dumps(supplier_template, indent=2, ensure_ascii=False))
            print()
            
            print("🎯 NEXT STEPS:")
            print("1. Share this RFQ with Turkish concrete admixture manufacturers")
            print("2. Key companies to contact:")
            print("   • Sika Turkey (www.sika.com.tr)")
            print("   • BASF Turkey Construction Chemicals")
            print("   • Akkim Construction Chemicals")
            print("   • Kalekim Chemical Solutions")
            print("   • MC-Bauchemie Turkey")
            print()
            print("3. Use the frontend to track responses and compare offers")
            print("4. Export data to Excel for detailed analysis")
            print()
            
            return rfq_id
            
        else:
            print(f"❌ RFQ Creation Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating RFQ: {e}")
        return None

def create_supplier_response_template():
    """Create an Excel-ready template for supplier responses"""
    print("📊 CREATING SUPPLIER RESPONSE EXCEL TEMPLATE")
    print("-" * 50)
    
    # Template structure you requested
    excel_columns = [
        "Tedarikçi Adı",
        "İlgili Kişi", 
        "E-posta",
        "Telefon",
        "Ürün",
        "Fiyat",
        "MOQ", 
        "Belgeler",
        "Teslim Süresi",
        "Ödeme Koşulları",
        "İhracat Deneyimi",
        "Notlar"
    ]
    
    print("Excel Column Headers:")
    for i, col in enumerate(excel_columns, 1):
        print(f"{i:2d}. {col}")
    
    print()
    print("📋 Sample Data Row:")
    sample_row = [
        "ABC Chemicals Ltd.",
        "Ahmet Yılmaz - Export Manager", 
        "export@abcchemicals.com.tr",
        "+90 232 XXX XXXX",
        "PCE Süperplastikleştirici",
        "4.50 USD/kg FOB Mersin",
        "1 ton",
        "ISO 9001, CE, TDS, SDS",
        "15-20 gün",
        "30% avans, 70% B/L karşılığı",
        "5+ yıl UAE deneyimi",
        "Teknik destek mevcut"
    ]
    
    for col, data in zip(excel_columns, sample_row):
        print(f"{col}: {data}")

if __name__ == "__main__":
    print("🚀 REAL BUSINESS RFQ CREATION")
    print("Moving from mock data to actual concrete admixture sourcing")
    print()
    
    rfq_id = create_real_concrete_admixture_rfq()
    
    if rfq_id:
        print()
        create_supplier_response_template()
        
        print()
        print("✅ REAL RFQ PROCESS INITIATED!")
        print("🌐 View in frontend dashboard to track responses")
        print("📧 Ready to send to potential suppliers")
        print("📊 Excel template ready for response compilation")