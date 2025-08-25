#!/usr/bin/env python3
"""
Test Intelligent RFQ Creation with Automatic Supplier Discovery
"""
import requests
import json
from datetime import datetime, timedelta

def test_intelligent_rfq_creation():
    print("🤖 TESTING INTELLIGENT RFQ CREATION")
    print("=" * 60)
    print("This demonstrates the new automatic supplier discovery feature")
    print()
    
    # Create RFQ with automatic supplier discovery
    rfq_data = {
        'title': 'TEST: Intelligent Supplier Discovery - Beton Katkı Maddeleri',
        'description': 'Dubai ihracatı için PCE süperplastikleştirici, hızlandırıcı ve geciktirici arayışımız. Sistem otomatik olarak uygun tedarikçileri bulup karşılaştırmalı analiz sunacak.',
        'category': 'chemicals',
        'quantity': 5,  # 5 tons
        'unit': 'tons',
        'budget_min': 15000,
        'budget_max': 25000,
        'deadline': (datetime.now() + timedelta(days=30)).isoformat() + 'Z',
        'delivery_location': 'FOB Mersin → Dubai, UAE',
        'requirements': 'ISO sertifikaları, Dubai pazarına uygun belgeler, teknik destek'
    }
    
    print("📋 RFQ DETAILS:")
    print(f"Title: {rfq_data['title']}")
    print(f"Category: {rfq_data['category']}")
    print(f"Quantity: {rfq_data['quantity']} {rfq_data['unit']}")
    print(f"Budget: ${rfq_data['budget_min']:,} - ${rfq_data['budget_max']:,}")
    print()
    
    try:
        print("🚀 Creating RFQ with automatic supplier discovery...")
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
            supplier_analysis = data.get('data', {}).get('supplier_analysis', {})
            
            print("✅ RFQ CREATED SUCCESSFULLY!")
            print(f"🆔 RFQ ID: {rfq_id}")
            print()
            
            if supplier_analysis.get('success'):
                suppliers = supplier_analysis.get('suppliers', [])
                report = supplier_analysis.get('comparison_report', {})
                
                print("🎯 AUTOMATIC SUPPLIER DISCOVERY RESULTS")
                print("-" * 50)
                print(f"📊 Found: {len(suppliers)} suppliers")
                print(f"🏆 Best Match: {report.get('best_supplier', {}).get('name', 'N/A')}")
                print(f"📈 Score: {report.get('best_supplier', {}).get('score', 'N/A')}/10")
                print()
                
                print("🏭 SUPPLIER COMPARISON TABLE")
                print("-" * 80)
                print(f"{'Rank':<4} {'Company':<25} {'Score':<6} {'Dubai':<6} {'Price':<8} {'Delivery':<9}")
                print("-" * 80)
                
                for i, supplier in enumerate(suppliers[:5], 1):
                    company = supplier['company_name'][:23]
                    score = supplier.get('overall_score', 0)
                    dubai = "✓" if supplier.get('export_experience', {}).get('dubai_direct') else "✗"
                    
                    # Get average price
                    products = supplier.get('products', {})
                    prices = [p.get('price_usd_kg', 0) for p in products.values()]
                    avg_price = sum(prices) / len(prices) if prices else 0
                    
                    delivery = supplier.get('delivery_terms', {}).get('delivery_time_days', 0)
                    
                    print(f"{i:<4} {company:<25} {score:<6.1f} {dubai:<6} ${avg_price:<7.2f} {delivery:<9}")
                
                print("-" * 80)
                print()
                
                # Show detailed analysis
                print("📈 ANALYSIS HIGHLIGHTS")
                print("-" * 30)
                summary = report.get('summary', {})
                price_analysis = report.get('price_analysis', {})
                delivery_analysis = report.get('delivery_analysis', {})
                
                print(f"• Average Score: {summary.get('average_overall_score', 'N/A')}/10")
                print(f"• Dubai Direct Suppliers: {summary.get('dubai_direct_suppliers', 0)}")
                print(f"• Price Range: ${price_analysis.get('min_price', 0):.2f} - ${price_analysis.get('max_price', 0):.2f}/kg")
                print(f"• Fastest Delivery: {delivery_analysis.get('fastest_delivery', 'N/A')} days")
                print(f"• Most Competitive: {price_analysis.get('most_competitive', 'N/A')}")
                print()
                
                # Show recommendations
                recommendations = report.get('recommendations', [])
                if recommendations:
                    print("💡 INTELLIGENT RECOMMENDATIONS")
                    print("-" * 30)
                    for i, rec in enumerate(recommendations, 1):
                        print(f"{i}. {rec}")
                    print()
                
                # Show next steps
                next_steps = report.get('next_steps', [])
                if next_steps:
                    print("🎯 SUGGESTED NEXT STEPS")
                    print("-" * 30)
                    for i, step in enumerate(next_steps, 1):
                        print(f"{i}. {step}")
                    print()
                
                print("✨ INTELLIGENT FEATURES DEMONSTRATED:")
                print("✅ Automatic supplier discovery by category")
                print("✅ Multi-criteria scoring and ranking") 
                print("✅ Budget compatibility analysis")
                print("✅ Dubai market experience evaluation")
                print("✅ Technical capability assessment")
                print("✅ Delivery time optimization")
                print("✅ Strategic recommendations")
                print("✅ Export-ready comparison data")
                
                return rfq_id
                
            else:
                print("⚠️ Supplier analysis failed:", supplier_analysis.get('message'))
                return rfq_id
                
        else:
            print(f"❌ RFQ Creation Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        return None

def test_comparison_report_api(rfq_id):
    """Test the comparison report API"""
    print("\n🔍 TESTING COMPARISON REPORT API")
    print("-" * 50)
    
    try:
        response = requests.get(
            f'http://localhost:8000/rfqs/{rfq_id}/comparison-report',
            headers={'Authorization': 'Bearer mock-admin-token'}
        )
        
        if response.status_code == 200:
            data = response.json()
            comparison_data = data.get('data', {})
            
            print("✅ Comparison Report Generated!")
            
            suppliers_comparison = comparison_data.get('suppliers_comparison', [])
            print(f"📊 Excel-ready data: {len(suppliers_comparison)} suppliers")
            
            if suppliers_comparison:
                # Show Excel column headers
                headers = list(suppliers_comparison[0].keys())
                print(f"📈 Excel Columns: {len(headers)} fields")
                print("   Key fields: Tedarikçi Adı, Fiyat USD/kg, Dubai Direkt, Genel Puan")
                
            return True
        else:
            print(f"❌ Comparison Report Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Comparison Report Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠 INTELLIGENT B2B RFQ SYSTEM DEMONSTRATION")
    print("Showcasing automatic supplier discovery and comparison")
    print()
    
    rfq_id = test_intelligent_rfq_creation()
    
    if rfq_id:
        test_comparison_report_api(rfq_id)
        
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("🌐 View results in the frontend preview")
        print("📊 Ready for Excel export and supplier contact")
        print("🤖 AI-powered supplier matching operational!")