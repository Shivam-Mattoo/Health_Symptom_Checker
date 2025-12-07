"""
Quick test for LLM service fix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import LLMService

print("=" * 60)
print("🧪 Testing LLM Service Fix")
print("=" * 60)

llm_service = LLMService()

# Test with different symptoms
test_cases = [
    "headache and fever for 3 days",
    "chest pain and shortness of breath",
    "what the issue"  # The problematic vague input
]

for symptoms in test_cases:
    print(f"\n{'=' * 60}")
    print(f"Testing: '{symptoms}'")
    print("=" * 60)
    
    result = llm_service.analyze_symptoms(symptoms, [])
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✅ Conditions ({len(result['conditions'])}):")
        for i, cond in enumerate(result['conditions'][:3], 1):
            print(f"   {i}. {cond}")
        
        print(f"\n✅ Recommendations ({len(result['recommendations'])}):")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n✅ Severity: {result['severity_assessment']}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)
