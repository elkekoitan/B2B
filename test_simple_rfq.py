#!/usr/bin/env python3
"""
Simple RFQ Test for Concrete Admixtures
"""

import requests
import json
from datetime import datetime, timedelta

def test_backend_connection():
    """Test if backend is responding"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        print(f"✅ Backend Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"❌ Backend Connection Failed: {e}")
        return False

def create_simple_concrete_rfq():
    """Create a simple RFQ for concrete admixtures"""
    
    rfq_data = {
        'title': 'Dubai Concrete Admixtures - PCE & Accelerators',
        'description': 'Sourcing concrete admixtures for Dubai construction projects. Need PCE superplasticizers, accelerators, and retarders from Turkish manufacturers.',
        'category': 'chemicals',
        'quantity': 2500,
        'unit': 'kg',
        'budget_min': 7000,
        'budget_max': 15000,
        'deadline': (datetime.now() + timedelta(days=30)).isoformat() + 'Z',
        'delivery_location': 'Dubai, UAE',
        'requirements': 'PCE superplasticizers, concrete accelerators, retarders. Dubai export experience preferred.'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/rfqs',
            headers={
                'Authorization': 'Bearer mock-admin-token',
                'Content-Type': 'application/json'
            },
            json=rfq_data,
            timeout=15
        )
        
        print(f"RFQ Creation Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            rfq_id = data.get('data', {}).get('rfq', {}).get('id', 'Unknown')
            print(f"✅ RFQ Created Successfully! ID: {rfq_id}")
            return rfq_id
        else:
            print(f"❌ RFQ Creation Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ RFQ Creation Error: {e}")
        return None

def main():
    print("🧪 TESTING BACKEND CONNECTION AND RFQ CREATION")
    print("=" * 50)
    
    # Test backend connection
    if test_backend_connection():
        # Create simple RFQ
        rfq_id = create_simple_concrete_rfq()
        
        if rfq_id:
            print(f"\n🎉 SUCCESS! RFQ created: {rfq_id}")
            print(f"🌐 Platform ready at: http://localhost:5174")
            print(f"📧 Ready to contact 103 suppliers!")
        else:
            print(f"\n❌ RFQ creation failed")
    else:
        print(f"\n❌ Backend not responding")

if __name__ == "__main__":
    main()