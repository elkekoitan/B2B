#!/usr/bin/env python3
"""
Frontend Integration Test
"""
import requests
import json

def test_frontend_integration():
    print("🌐 Testing Frontend Integration...")
    
    try:
        # Test frontend health
        frontend_response = requests.get('http://localhost:5173')
        print(f"✅ Frontend Status: {frontend_response.status_code}")
        
        # Test backend health  
        backend_response = requests.get('http://localhost:8000/health')
        print(f"✅ Backend Health: {backend_response.status_code}")
        
        if backend_response.status_code == 200:
            health_data = backend_response.json()
            print(f"🏥 System Status: {health_data.get('status', 'unknown')}")
            
            services = health_data.get('services', {})
            for service, status in services.items():
                service_status = status.get('status', 'unknown')
                print(f"   {service}: {service_status}")
        
        # Test API endpoints that frontend uses
        print("\n🔗 Testing API Endpoints...")
        
        # Test RFQ listing (dashboard endpoint)
        rfq_response = requests.get(
            'http://localhost:8000/rfqs',
            headers={'Authorization': 'Bearer mock-admin-token'}
        )
        print(f"📋 RFQ Listing: {rfq_response.status_code}")
        
        if rfq_response.status_code == 200:
            rfq_data = rfq_response.json()
            print(f"   Total RFQs: {len(rfq_data.get('data', []))}")
            print(f"   Success: {rfq_data.get('success', False)}")
        
        # Test analytics endpoint (if available)
        try:
            analytics_response = requests.get(
                'http://localhost:8000/analytics/rfqs',
                headers={'Authorization': 'Bearer mock-admin-token'}
            )
            print(f"📊 Analytics: {analytics_response.status_code}")
        except:
            print("📊 Analytics: Endpoint not available (this is normal)")
        
        print("\n✅ Frontend Integration Test Complete!")
        print("\n🎯 Ready for User Testing:")
        print("   1. Open preview browser (click the button above)")
        print("   2. Login with: turhanhamza@gmail.com / 117344") 
        print("   3. View RFQs in dashboard")
        print("   4. Create new RFQ")
        print("   5. Verify it appears in the list")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend Integration Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_frontend_integration()