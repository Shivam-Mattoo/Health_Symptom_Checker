"""
Quick MongoDB Connection Test
Tests the MongoDB connection independently
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

print("=" * 70)
print("🧪 MongoDB Connection Test")
print("=" * 70)

if not MONGO_URI:
    print("❌ MONGO_URI not found in .env file")
    exit(1)

print(f"\n📋 Connection String: {MONGO_URI[:50]}...")
print("\n🔌 Attempting to connect...")

try:
    # Add tlsAllowInvalidCertificates for Python 3.13
    connection_string = MONGO_URI
    if "?" in connection_string:
        connection_string += "&tlsAllowInvalidCertificates=true"
    else:
        connection_string += "?tlsAllowInvalidCertificates=true"
    
    client = MongoClient(
        connection_string,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=20000
    )
    
    # Test connection
    client.admin.command('ping')
    
    print("✅ SUCCESS! MongoDB connection works!")
    print(f"✅ Server Info: {client.server_info()['version']}")
    
    # Test database access
    db = client['health_symptom_checker']
    print(f"✅ Database access: {db.name}")
    
    # List collections
    collections = db.list_collection_names()
    print(f"✅ Collections: {collections if collections else 'None (will be created on first use)'}")
    
    client.close()
    print("\n" + "=" * 70)
    print("🎉 All tests passed! MongoDB is ready to use.")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ CONNECTION FAILED!")
    print(f"❌ Error: {e}")
    print(f"❌ Error Type: {type(e).__name__}")
    
    print("\n" + "=" * 70)
    print("💡 Quick Fixes:")
    print("=" * 70)
    print("1. Check MongoDB Atlas Network Access (allow 0.0.0.0/0)")
    print("2. Verify MONGO_URI in .env file")
    print("3. Run PowerShell as Admin and execute:")
    print("   netsh winsock reset")
    print("   ipconfig /flushdns")
    print("4. Restart your computer")
    print("=" * 70)
    exit(1)
