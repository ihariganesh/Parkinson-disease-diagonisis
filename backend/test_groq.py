#!/usr/bin/env python3
"""Test Groq AI service"""
import os
import sys
sys.path.append('/home/hari/Downloads/parkinson/parkinson-app/backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("GROQ AI SERVICE TEST")
print("=" * 60)

# Check if Groq API key exists
groq_key = os.getenv('GROQ_API_KEY', '')
print(f"\n1. GROQ_API_KEY found: {bool(groq_key)}")
if groq_key:
    print(f"   Key preview: {groq_key[:20]}...***")

# Try importing Groq
try:
    from groq import Groq
    print("✅ 2. Groq library imported successfully")
    
    # Try creating client
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            print("✅ 3. Groq client created successfully")
            
            # Try a simple completion
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say 'Groq is working!' in one sentence."}
                    ],
                    max_tokens=50
                )
                response = completion.choices[0].message.content
                print(f"✅ 4. Groq API call successful!")
                print(f"   Response: {response}")
                print("\n" + "=" * 60)
                print("✅ GROQ IS FULLY FUNCTIONAL!")
                print("=" * 60)
            except Exception as e:
                print(f"❌ 4. Groq API call failed: {e}")
        except Exception as e:
            print(f"❌ 3. Groq client creation failed: {e}")
    else:
        print("⚠️ 3. No API key to test")
        
except ImportError as e:
    print(f"❌ 2. Groq library not installed: {e}")
    print("\n💡 Install with: pip install groq")

# Test AI service
print("\n" + "=" * 60)
print("TESTING AI SERVICE")
print("=" * 60)

try:
    from app.services.ai_service import get_ai_service
    ai_service = get_ai_service()
    print(f"✅ AI Service initialized")
    print(f"   Providers: {len(ai_service.providers)}")
    for provider in ai_service.providers:
        print(f"   - {provider['name']} ({provider['type']})")
except Exception as e:
    print(f"❌ AI Service initialization failed: {e}")
    import traceback
    traceback.print_exc()
