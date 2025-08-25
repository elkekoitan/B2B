#!/usr/bin/env python3
"""
Admin User Creation Script for Agentik B2B Platform
Creates an admin user with the specified credentials.
"""

import json
import uuid
from datetime import datetime
import hashlib
import os
import sys

# Admin user details
ADMIN_EMAIL = "turhanhamza@gmail.com"
ADMIN_PASSWORD = "117344"
ADMIN_NAME = "Turhan Hamza"

def create_mock_admin_user():
    """Create admin user entry for the mock system"""
    
    # Generate a unique user ID
    user_id = str(uuid.uuid4())
    auth_user_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    
    # Create user data
    admin_user = {
        "id": user_id,
        "auth_user_id": auth_user_id,
        "email": ADMIN_EMAIL,
        "full_name": ADMIN_NAME,
        "company_name": "Agentik Admin",
        "phone": "",
        "is_admin": True,
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create company data
    admin_company = {
        "id": company_id,
        "name": "Agentik Admin",
        "email": ADMIN_EMAIL,
        "phone": "",
        "address": "",
        "website": "",
        "industry": "Technology",
        "tax_number": "",
        "contact_person": ADMIN_NAME,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create auth credentials for mock authentication
    auth_user = {
        "id": auth_user_id,
        "email": ADMIN_EMAIL,
        "password_hash": hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
        "email_confirmed": True,
        "created_at": datetime.utcnow().isoformat(),
        "user_metadata": {
            "full_name": ADMIN_NAME,
            "company_name": "Agentik Admin"
        }
    }
    
    return admin_user, admin_company, auth_user

def save_mock_data():
    """Save admin user data to JSON files for the mock system"""
    
    admin_user, admin_company, auth_user = create_mock_admin_user()
    
    # Create data directory if it doesn't exist
    data_dir = "mock_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Save user data
    with open(os.path.join(data_dir, "admin_user.json"), "w", encoding="utf-8") as f:
        json.dump(admin_user, f, indent=2, ensure_ascii=False)
    
    # Save company data
    with open(os.path.join(data_dir, "admin_company.json"), "w", encoding="utf-8") as f:
        json.dump(admin_company, f, indent=2, ensure_ascii=False)
    
    # Save auth data
    with open(os.path.join(data_dir, "admin_auth.json"), "w", encoding="utf-8") as f:
        json.dump(auth_user, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Admin user created successfully!")
    print(f"📧 Email: {ADMIN_EMAIL}")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print(f"👤 Name: {ADMIN_NAME}")
    print(f"🏢 Company: Agentik Admin")
    print(f"⚡ Admin privileges: Yes")
    print(f"📁 Data saved to: {data_dir}/")
    print()
    print("🌐 You can now login to the frontend at http://localhost:5176")
    print("🔒 Use the credentials above to access the admin panel")

def update_auth_context():
    """Update the AuthContext to include the admin user for mock authentication"""
    
    auth_context_path = "frontend/src/contexts/AuthContext.tsx"
    
    if not os.path.exists(auth_context_path):
        print(f"⚠️  Warning: {auth_context_path} not found")
        return
    
    admin_user, admin_company, auth_user = create_mock_admin_user()
    
    # Create a simple mock auth snippet
    mock_auth_snippet = f'''
// Mock admin user for development
const MOCK_ADMIN_USER = {json.dumps(admin_user, indent=2)};

const MOCK_AUTH_USER = {json.dumps(auth_user, indent=2)};
'''
    
    print("📝 Mock admin user data generated")
    print("💡 To integrate with the frontend, add this data to your AuthContext or mock authentication system:")
    print(mock_auth_snippet)

if __name__ == "__main__":
    print("🚀 Creating admin user for Agentik B2B Platform...")
    print("=" * 60)
    
    try:
        save_mock_data()
        update_auth_context()
        
        print("=" * 60)
        print("✨ Admin user setup completed successfully!")
        print("🎯 Next steps:")
        print("   1. Start the frontend: http://localhost:5176")
        print("   2. Login with the credentials above")
        print("   3. Access the admin panel")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        sys.exit(1)