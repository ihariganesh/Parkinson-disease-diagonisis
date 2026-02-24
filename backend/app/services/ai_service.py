"""
Unified AI Service supporting multiple providers (NVIDIA NIM Kimi, Groq, Gemini)
Automatically selects best available provider
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MultiProviderAIService:
    """AI service that supports multiple providers with automatic fallback"""
    
    def __init__(self):
        """Initialize all available AI providers"""
        self.providers: List[Dict[str, Any]] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured AI providers - NVIDIA NIM Kimi preferred"""
        
        # OpenRouter as PRIMARY provider
        or_key = os.getenv('OPENROUTER_API_KEY', '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')
        if or_key:
            try:
                self.providers.append({
                    'name': 'OpenRouter',
                    'api_key': or_key,
                    'type': 'openrouter',
                    'base_url': 'https://openrouter.ai/api/v1/chat/completions',
                    'models': [
                        'meta-llama/llama-3.3-70b-instruct:free',
                        'google/gemini-2.0-flash-exp:free',
                        'deepseek/deepseek-r1:free',
                    ]
                })
                print(f"✅ OpenRouter initialized (PRIMARY PROVIDER) with key: {or_key[:12]}...***")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenRouter: {e}")
        else:
            print("⚠️ OPENROUTER_API_KEY not found - OpenRouter provider unavailable")
        
        # Groq as secondary provider
        groq_key = os.getenv('GROQ_API_KEY', '')
        if groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                self.providers.append({
                    'name': 'Groq (Secondary)',
                    'client': client,
                    'type': 'groq',
                    'models': ['llama-3.3-70b-versatile', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768']
                })
                print(f"✅ Groq AI initialized (SECONDARY PROVIDER) with key: {groq_key[:20]}...***")
            except Exception as e:
                print(f"⚠️ Failed to initialize Groq: {e}")
        else:
            print("⚠️ GROQ_API_KEY not found - Groq provider unavailable")
        
        # Gemini as backup only (disabled by default unless ENABLE_GEMINI=true)
        enable_gemini = os.getenv('ENABLE_GEMINI', 'false').lower() == 'true'
        if enable_gemini:
            gemini_keys_str = os.getenv('GEMINI_API_KEY', '')
            if gemini_keys_str:
                try:
                    import google.generativeai as genai
                    gemini_keys = [k.strip() for k in gemini_keys_str.split(',') if k.strip()]
                    
                    for i, key in enumerate(gemini_keys):
                        try:
                            genai.configure(api_key=key)
                            model = genai.GenerativeModel('gemini-2.0-flash-exp')
                            self.providers.append({
                                'name': f'Gemini #{i+1} (Backup)',
                                'client': model,
                                'type': 'gemini',
                                'api_key': key,
                                'models': ['gemini-2.0-flash-exp']
                            })
                            print(f"✅ Gemini AI #{i+1} initialized as backup")
                        except Exception as e:
                            print(f"⚠️ Failed to initialize Gemini key #{i+1}: {str(e)[:100]}")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Gemini: {e}")
        else:
            print("ℹ️ Gemini disabled (set ENABLE_GEMINI=true to enable)")
        
        if not self.providers:
            print("❌ No AI providers available - will use fallback recommendations")
        else:
            primary = self.providers[0]['name'] if self.providers else 'None'
            print(f"✅ Initialized {len(self.providers)} AI provider(s) - Primary: {primary}")
    
    async def generate_recommendations(
        self,
        diagnosis: str,
        pd_probability: float,
        confidence: float,
        age: int,
        gender: str = 'not_specified',
        location: Optional[Dict[str, Any]] = None,
        severity: str = 'Unknown',
        stage: int = 0,
        symptoms: Optional[Dict[str, Any]] = None,
        medical_history: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate recommendations using best available provider"""
        
        if not self.providers:
            return self._get_fallback_recommendations(diagnosis, age)
        
        # Build prompt
        prompt = self._build_prompt(
            diagnosis, pd_probability, confidence, age, gender,
            location, severity, stage, symptoms, medical_history
        )
        
        # Try each provider in order
        for provider in self.providers:
            try:
                print(f"🔄 Trying provider: {provider['name']}")
                
                if provider['type'] == 'openrouter':
                    response = await self._generate_with_openrouter(provider, prompt)
                elif provider['type'] == 'groq':
                    response = await self._generate_with_groq(provider, prompt)
                elif provider['type'] == 'gemini':
                    response = await self._generate_with_gemini(provider, prompt)
                else:
                    continue
                
                # Parse response
                recommendations = self._parse_recommendations(response)
                
                # Add metadata
                recommendations['metadata'] = {
                    'generated_at': datetime.now().isoformat(),
                    'provider': provider['name'],
                    'source': 'ai',  # Mark as AI-generated
                    'diagnosis': diagnosis,
                    'pd_probability': pd_probability,
                    'confidence': confidence,
                    'age': age,
                    'gender': gender,
                    'location': location,
                    'severity': severity,
                    'stage': stage
                }
                
                print(f"✅ Successfully generated recommendations with {provider['name']}")
                return recommendations
                
            except Exception as e:
                error_str = str(e).lower()
                print(f"❌ {provider['name']} failed: {str(e)[:150]}")
                
                # Check if quota/rate limit error
                if any(word in error_str for word in ['quota', 'rate limit', '429', 'exceeded']):
                    print(f"   Quota exceeded for {provider['name']}, trying next provider...")
                    continue
                else:
                    print(f"   Unexpected error, trying next provider...")
                    continue
        
        # All providers failed - use fallback
        print("⚠️ All AI providers failed - using fallback recommendations")
        return self._get_fallback_recommendations(diagnosis, age)
    
    async def _generate_with_openrouter(self, provider: Dict[str, Any], prompt: str) -> str:
        """Generate with OpenRouter API"""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "HTTP-Referer": "http://localhost:5173", # Optional, for OpenRouter rankings
            "X-Title": "ParkinsonCare", # Optional, for OpenRouter rankings
            "Content-Type": "application/json"
        }
        
        last_error = None
        async with httpx.AsyncClient() as client:
            for current_model in provider['models']:
                try:
                    payload = {
                        "model": current_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert neurologist and lifestyle medicine specialist. Generate comprehensive, personalized lifestyle recommendations in valid JSON format. Always respond with ONLY a valid JSON object, no markdown formatting."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 4096,
                        "temperature": 0.7,
                        "stream": False,
                        "provider": {
                            "data_collection": "allow",
                            "allow_fallbacks": True
                        }
                    }
                    
                    print(f"🔄 Calling OpenRouter API (model={current_model})...")
                    response = await client.post(
                        provider['base_url'],
                        headers=headers,
                        json=payload,
                        timeout=180.0
                    )
                    
                    if response.status_code != 200:
                        error_detail = response.text[:300]
                        raise Exception(f"OpenRouter API error {response.status_code}: {error_detail}")
                    
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Strip markdown code blocks just in case
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    
                    content = content.strip()
                    
                    if not content:
                        raise Exception(f"OpenRouter model {current_model} returned empty response")
                    
                    print(f"✅ OpenRouter response received from {current_model} ({len(content)} chars)")
                    return content
                    
                except Exception as e:
                    print(f"⚠️ OpenRouter model {current_model} failed: {e}")
                    last_error = e
                    continue
                    
        raise Exception(f"All OpenRouter models failed. Last error: {last_error}")
    
    async def _generate_with_groq(self, provider: Dict[str, Any], prompt: str) -> str:
        """Generate with Groq API"""
        client = provider['client']
        model = provider['models'][0]
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert neurologist and lifestyle medicine specialist. Generate comprehensive, personalized lifestyle recommendations in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2048,
            top_p=0.8,
            response_format={"type": "json_object"}
        )
        
        return completion.choices[0].message.content
    
    async def _generate_with_gemini(self, provider: Dict[str, Any], prompt: str) -> str:
        """Generate with Gemini API"""
        import google.generativeai as genai
        
        model = provider['client']
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        
        return response.text
    
    def _build_prompt(
        self,
        diagnosis: str,
        pd_probability: float,
        confidence: float,
        age: int,
        gender: str,
        location: Optional[Dict[str, Any]],
        severity: str,
        stage: int,
        symptoms: Optional[Dict[str, Any]],
        medical_history: Optional[str]
    ) -> str:
        """Build comprehensive prompt"""
        
        location_text = 'Not specified'
        if location:
            parts = []
            if location.get('city'): parts.append(location['city'])
            if location.get('state'): parts.append(location['state'])
            if location.get('country'): parts.append(location['country'])
            location_text = ', '.join(parts) if parts else 'Not specified'
        
        symptoms_text = f"\n\nDetected Symptoms:\n{json.dumps(symptoms, indent=2)}" if symptoms else ""
        history_text = f"\n\nMedical History:\n{medical_history}" if medical_history else ""
        
        prompt = f"""
You are an expert neurologist and lifestyle medicine specialist. Generate comprehensive, personalized lifestyle recommendations for a patient with the following profile:

**Patient Demographics:**
- Age: {age} years
- Gender: {gender}
- Location: {location_text}

**Diagnosis Information:**
- Final Diagnosis: {diagnosis}
- Parkinson's Probability: {pd_probability:.1f}%
- Confidence Level: {confidence:.1f}%
- Severity: {severity}
- Stage: {stage} (0=Healthy, 1=Early, 2=Moderate, 3=Advanced){symptoms_text}{history_text}

**Task:**
Generate personalized lifestyle recommendations across 7 categories:

1. **Exercise** - Physical activities, frequency, specific exercises
2. **Nutrition** - Diet recommendations, foods to eat/avoid
3. **Mental Health** - Stress management, emotional wellbeing
4. **Sleep** - Sleep hygiene, routines
5. **Daily Living** - Adaptive strategies, routines
6. **Medical Management** - Doctor visits, medication adherence
7. **Technology & Support** - Apps, devices, support groups

**Requirements:**
- 3-5 specific, actionable recommendations per category
- Include WHY each recommendation is beneficial
- Evidence-based practices
- Clear, compassionate language
- Consider patient's age and diagnosis severity

Return ONLY a valid JSON object with this EXACT structure:
{{
  "exercise": [
    {{"title": "...", "description": "...", "frequency": "...", "benefits": "..."}},
    ...
  ],
  "nutrition": [...],
  "mental_health": [...],
  "sleep": [...],
  "daily_living": [...],
  "medical_management": [...],
  "technology_support": [...]
}}
"""
        return prompt
    
    def _parse_recommendations(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            recommendations = json.loads(json_text)
            
            # Validate required keys
            required_keys = [
                'exercise', 'nutrition', 'mental_health',
                'sleep', 'daily_living', 'medical_management', 'technology_support'
            ]
            
            for key in required_keys:
                if key not in recommendations:
                    recommendations[key] = []
            
            return recommendations
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return self._create_fallback_structure(response_text)
    
    def _create_fallback_structure(self, text: str) -> Dict[str, Any]:
        """Create structured recommendations from unstructured text"""
        return {
            'exercise': [],
            'nutrition': [],
            'mental_health': [],
            'sleep': [],
            'daily_living': [],
            'medical_management': [],
            'technology_support': [],
            'general': [{
                'title': 'General Recommendations',
                'description': text[:1000],
                'benefits': 'AI-generated comprehensive guidance'
            }]
        }
    
    def _get_fallback_recommendations(self, diagnosis: str, age: int) -> Dict[str, Any]:
        """Provide fallback recommendations if AI fails"""
        
        is_pd = 'parkinson' in diagnosis.lower()
        
        return {
            'exercise': [
                {
                    'title': 'Regular Physical Activity',
                    'description': f"Engage in {'specialized Parkinson\'s exercise programs' if is_pd else 'moderate exercise'} for 30 minutes daily",
                    'frequency': '5-7 days per week',
                    'benefits': 'Improves mobility, balance, and overall health'
                },
                {
                    'title': 'Balance Training',
                    'description': 'Practice balance exercises like tai chi or yoga',
                    'frequency': '3-4 times per week',
                    'benefits': 'Reduces fall risk and improves stability'
                }
            ],
            'nutrition': [
                {
                    'title': 'Mediterranean Diet',
                    'description': 'Follow a Mediterranean-style diet rich in fruits, vegetables, and omega-3 fatty acids',
                    'frequency': 'Daily',
                    'benefits': 'Supports brain health and reduces inflammation'
                },
                {
                    'title': 'Adequate Hydration',
                    'description': 'Drink 6-8 glasses of water daily',
                    'frequency': 'Throughout the day',
                    'benefits': 'Maintains overall health and prevents constipation'
                }
            ],
            'mental_health': [
                {
                    'title': 'Stress Management',
                    'description': 'Practice mindfulness meditation or deep breathing exercises',
                    'frequency': 'Daily, 10-15 minutes',
                    'benefits': 'Reduces anxiety and improves emotional well-being'
                }
            ],
            'sleep': [
                {
                    'title': 'Consistent Sleep Schedule',
                    'description': 'Go to bed and wake up at the same time daily',
                    'frequency': 'Daily',
                    'benefits': 'Improves sleep quality and overall health'
                }
            ],
            'daily_living': [
                {
                    'title': 'Structured Routine',
                    'description': 'Maintain a consistent daily routine for activities',
                    'frequency': 'Daily',
                    'benefits': 'Reduces stress and improves symptom management'
                }
            ],
            'medical_management': [
                {
                    'title': 'Regular Check-ups',
                    'description': f"{'Consult neurologist every 3-6 months' if is_pd else 'Annual health check-ups'}",
                    'frequency': f"{'Every 3-6 months' if is_pd else 'Annually'}",
                    'benefits': 'Monitors progression and adjusts treatment as needed'
                }
            ],
            'technology_support': [
                {
                    'title': 'Health Tracking Apps',
                    'description': 'Use smartphone apps to track symptoms and medication',
                    'frequency': 'Daily',
                    'benefits': 'Provides valuable data for healthcare providers'
                }
            ],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'diagnosis': diagnosis,
                'age': age,
                'source': 'fallback_recommendations'
            }
        }


# Singleton instance
_ai_service: Optional[MultiProviderAIService] = None


def get_ai_service() -> MultiProviderAIService:
    """Get or create singleton AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = MultiProviderAIService()
    return _ai_service
