"""
Test Voice Analysis Endpoint with Real Features
"""

import requests
import json

def test_voice_endpoint():
    """Test the voice analysis endpoint"""
    
    print("=" * 70)
    print("TESTING VOICE ANALYSIS API ENDPOINT")
    print("=" * 70)
    
    # API endpoint - Using demo endpoint (no auth required)
    url = "http://localhost:8000/api/v1/analysis/speech/demo-analyze"
    
    # Test audio file
    audio_file = "/home/hari/Downloads/parkinson/test_audio.wav"
    
    print(f"\n1. Testing endpoint: {url}")
    print(f"2. Audio file: {audio_file}")
    print("-" * 70)
    
    try:
        # Upload file
        with open(audio_file, 'rb') as f:
            files = {'file': ('test_audio.wav', f, 'audio/wav')}
            
            print("\n3. Sending request...")
            response = requests.post(url, files=files, timeout=60)
            
            print(f"4. Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n5. Analysis Results:")
                print("-" * 70)
                print(json.dumps(result, indent=2))
                
                # Check if using real features
                note = result.get('note', '')
                if 'Real acoustic features' in note or 'extracted' in note.lower():
                    print("\n✅ SUCCESS! Using real feature extraction!")
                elif 'simulated' in note.lower() or 'mock' in note.lower():
                    print("\n⚠️  WARNING: Still using simulated features")
                else:
                    print(f"\n❓ Note: {note}")
                
                return True
            else:
                print(f"\n❌ Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_voice_endpoint()
