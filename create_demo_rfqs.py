#!/usr/bin/env python3
"""
Create Multiple Test RFQs for Demonstration
"""
import requests
import json
from datetime import datetime, timedelta

def create_test_rfqs():
    print("🚀 Creating Multiple Test RFQs...")
    
    test_rfqs = [
        {
            'title': 'Office Furniture Supply - Masalar ve Sandalyeler',
            'description': '50 adet masa ve 200 adet ofis sandalyesi tedariki gerekiyor. Ergonomik tasarım tercih edilir.',
            'category': 'furniture',
            'quantity': 250,
            'unit': 'pieces',
            'budget_min': 15000,
            'budget_max': 25000,
            'deadline': (datetime.now() + timedelta(days=30)).isoformat() + 'Z',
            'delivery_location': 'Ankara, Turkey',
            'requirements': 'ISO 9001 kalite belgesi, 2 yıl garanti'
        },
        {
            'title': 'Industrial Machinery Parts - Yedek Parça',
            'description': 'Fabrika makineleri için kritik yedek parça ihtiyacı. Hızlı teslimat gerekli.',
            'category': 'machinery',
            'quantity': 25,
            'unit': 'sets',
            'budget_min': 8000,
            'budget_max': 12000,
            'deadline': (datetime.now() + timedelta(days=15)).isoformat() + 'Z',
            'delivery_location': 'Bursa, Turkey',
            'requirements': 'Acil teslimat, orijinal parça belgesi gerekli'
        },
        {
            'title': 'Chemical Raw Materials - Kimyasal Hammadde',
            'description': 'Üretim sürecinde kullanılacak kimyasal hammaddeler. Kalite sertifikaları şart.',
            'category': 'chemicals',
            'quantity': 5000,
            'unit': 'kg',
            'budget_min': 20000,
            'budget_max': 35000,
            'deadline': (datetime.now() + timedelta(days=60)).isoformat() + 'Z',
            'delivery_location': 'Izmir, Turkey',
            'requirements': 'MSDS belgesi, laboratuvar test raporu'
        }
    ]
    
    created_rfqs = []
    
    for i, rfq_data in enumerate(test_rfqs, 1):
        print(f"\n📝 Creating RFQ {i}: {rfq_data['title'][:50]}...")
        
        try:
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
                created_rfqs.append(rfq_id)
                print(f"   ✅ Success! ID: {rfq_id}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # List all RFQs
    print(f"\n🔍 Listing All RFQs...")
    try:
        list_response = requests.get(
            'http://localhost:8000/rfqs',
            headers={'Authorization': 'Bearer mock-admin-token'}
        )
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            rfqs = list_data.get('data', [])
            
            print(f"📊 Total RFQs: {len(rfqs)}")
            print("=" * 60)
            
            for i, rfq in enumerate(rfqs, 1):
                print(f"{i}. {rfq['title']}")
                print(f"   📂 Category: {rfq['category']}")
                print(f"   📦 Quantity: {rfq['quantity']} {rfq['unit']}")
                print(f"   💰 Budget: ${rfq.get('budget_min', 0):,.0f} - ${rfq.get('budget_max', 0):,.0f}")
                print(f"   📍 Location: {rfq['delivery_location']}")
                print(f"   🏷️  Status: {rfq['status']}")
                print()
            
            print("✅ RFQ Creation Demo Complete!")
            print("🎯 Ready for frontend testing!")
            
        else:
            print(f"❌ Listing failed: {list_response.status_code}")
            
    except Exception as e:
        print(f"❌ Listing error: {e}")

if __name__ == "__main__":
    create_test_rfqs()