#!/usr/bin/env python3
"""
Test RFQ Creation Script
"""
import requests
import json
from datetime import datetime, timedelta

def test_rfq_creation():
    # Test RFQ data with Turkish content
    rfq_data = {
        'title': 'Elektronik Komponent Tedariki - Test',
        'description': 'Bu test RFQ\'su ile sistemin çalışıp çalışmadığını kontrol ediyoruz. 500 adet yüksek kalite elektronik komponent ihtiyacımız var. Ürünler CE sertifikalı olmalı.',
        'category': 'electronics',
        'quantity': 500,
        'unit': 'pieces',
        'budget_min': 2500,
        'budget_max': 8000,
        'deadline': (datetime.now() + timedelta(days=45)).isoformat() + 'Z',
        'delivery_location': 'Istanbul, Turkey',
        'requirements': 'CE sertifikası gerekli, test raporu ile birlikte teslim edilmeli'
    }
    
    print("🚀 Testing RFQ Creation...")
    print(f"📝 Title: {rfq_data['title']}")
    print(f"📊 Quantity: {rfq_data['quantity']} {rfq_data['unit']}")
    print(f"💰 Budget: ${rfq_data['budget_min']} - ${rfq_data['budget_max']}")
    
    try:
        response = requests.post(
            'http://localhost:8000/rfqs',
            headers={
                'Authorization': 'Bearer mock-admin-token',
                'Content-Type': 'application/json'
            },
            json=rfq_data
        )
        
        print(f"\n✅ RFQ Creation Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            rfq_id = data.get('data', {}).get('rfq', {}).get('id', 'Not found')
            print(f"📋 Message: {data.get('message', 'Success')}")
            print(f"🆔 RFQ ID: {rfq_id}")
            print(f"📅 Created: {data.get('data', {}).get('rfq', {}).get('created_at', 'Unknown')}")
            
            # Test listing RFQs
            print("\n🔍 Testing RFQ Listing...")
            list_response = requests.get(
                'http://localhost:8000/rfqs',
                headers={'Authorization': 'Bearer mock-admin-token'}
            )
            
            if list_response.status_code == 200:
                list_data = list_response.json()
                rfq_count = len(list_data.get('data', []))
                print(f"📊 Total RFQs: {rfq_count}")
                print(f"📄 Page: {list_data.get('page', 1)} of {list_data.get('total', 0)} total items")
                
                # Show latest RFQ
                if list_data.get('data'):
                    latest_rfq = list_data['data'][0]
                    print(f"\n📋 Latest RFQ:")
                    print(f"   Title: {latest_rfq.get('title', 'N/A')}")
                    print(f"   Status: {latest_rfq.get('status', 'N/A')}")
                    print(f"   Category: {latest_rfq.get('category', 'N/A')}")
                    
                print("\n✅ RFQ Creation and Listing Test PASSED!")
                return True
            else:
                print(f"❌ RFQ Listing Failed: {list_response.status_code}")
                print(f"Error: {list_response.text}")
                return False
        else:
            print(f"❌ RFQ Creation Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
        return False

if __name__ == "__main__":
    test_rfq_creation()