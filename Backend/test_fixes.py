"""
Test script to verify all fixes are working:
1. Pinecone dimension fix (384 instead of 1024)
2. Gemini model fix (gemini-2.0-flash-exp)
3. New Google Genai SDK integration
"""

import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🧪 TESTING ALL FIXES")
print("=" * 60)

# Test 1: Pinecone Service
print("\n1️⃣ Testing Pinecone Service...")
print("-" * 60)
try:
    from services.pinecone_service import PineconeService
    pinecone_service = PineconeService()
    
    # Test embedding generation
    test_text = "headache and fever"
    embedding = pinecone_service.generate_embedding(test_text)
    print(f"✅ Embedding generated successfully!")
    print(f"   Dimension: {len(embedding)}")
    print(f"   Expected: 384")
    
    if len(embedding) == 384:
        print("   ✅ PASS: Dimension matches!")
    else:
        print(f"   ❌ FAIL: Dimension mismatch! Got {len(embedding)}, expected 384")
        
except Exception as e:
    print(f"❌ Pinecone test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: LLM Service
print("\n2️⃣ Testing LLM Service (Gemini)...")
print("-" * 60)
try:
    from services.llm_service import LLMService
    llm_service = LLMService()
    print("✅ LLM Service initialized successfully!")
    print(f"   Model: {llm_service.llm.model_name}")
    
    # Test simple analysis
    print("\n   Testing symptom analysis...")
    result = llm_service.analyze_symptoms("headache", [])
    
    if result and not result.get("error"):
        print("   ✅ PASS: LLM analysis working!")
        print(f"   Conditions found: {len(result.get('conditions', []))}")
    else:
        print(f"   ❌ FAIL: LLM analysis failed - {result.get('error')}")
        
except Exception as e:
    print(f"❌ LLM test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Google Genai SDK (direct test)
print("\n3️⃣ Testing Google Genai SDK (Direct)...")
print("-" * 60)
try:
    from google import genai
    from google.genai import types
    from config import Config
    
    client = genai.Client(api_key=Config.GEMINI_KEY)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", 
        contents="What is a headache? Answer in one sentence.",
        config=types.GenerateContentConfig(
            max_output_tokens=100,
        )
    )
    
    print(f"✅ Direct Genai SDK working!")
    print(f"   Response: {response.text[:100]}...")
    
except Exception as e:
    print(f"❌ Genai SDK test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 TESTING COMPLETE")
print("=" * 60)
