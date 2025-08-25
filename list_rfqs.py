import requests

# Get current RFQs
response = requests.get(
    'http://localhost:8000/rfqs', 
    headers={'Authorization': 'Bearer mock-admin-token'}
)

if response.status_code == 200:
    data = response.json()
    rfqs = data.get('data', [])
    
    print('📋 Current RFQs in System:')
    print('=' * 50)
    
    for i, rfq in enumerate(rfqs):
        print(f'{i+1}. {rfq["title"]}')
        print(f'   Status: {rfq["status"]}')
        print(f'   Category: {rfq["category"]}')
        print(f'   Quantity: {rfq["quantity"]} {rfq["unit"]}')
        print(f'   Created: {rfq["created_at"][:10]}')
        print()
    
    print(f'Total: {len(rfqs)} RFQs')
else:
    print(f'Error: {response.status_code}')