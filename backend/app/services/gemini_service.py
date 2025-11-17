"""
Google Gemini AI Service for Lifestyle Recommendations
Generates personalized lifestyle recommendations based on Parkinson's diagnosis
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai


class GeminiLifestyleService:
    """Service for generating AI-powered lifestyle recommendations using Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini AI service
        
        Args:
            api_key: Google Gemini API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', 'AIzaSyDA4lY5XN0QnX-sp_IBG5ZaXreIZGnd-rM')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI service initialized")
    
    async def generate_recommendations(
        self,
        diagnosis: str,
        pd_probability: float,
        confidence: float,
        age: int,
        symptoms: Optional[Dict[str, Any]] = None,
        medical_history: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized lifestyle recommendations
        
        Args:
            diagnosis: Final diagnosis (e.g., "Healthy", "Early Stage Parkinson's")
            pd_probability: Parkinson's disease probability (0-100)
            confidence: Model confidence level (0-100)
            age: Patient age
            symptoms: Dictionary of detected symptoms
            medical_history: Additional medical history
            
        Returns:
            Dictionary containing categorized recommendations
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_prompt(
                diagnosis, pd_probability, confidence, age, symptoms, medical_history
            )
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            # Parse and structure response
            recommendations = self._parse_recommendations(response.text)
            
            # Add metadata
            recommendations['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'diagnosis': diagnosis,
                'pd_probability': pd_probability,
                'confidence': confidence,
                'age': age
            }
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._get_fallback_recommendations(diagnosis, age)
    
    def _build_prompt(
        self,
        diagnosis: str,
        pd_probability: float,
        confidence: float,
        age: int,
        symptoms: Optional[Dict[str, Any]],
        medical_history: Optional[str]
    ) -> str:
        """Build comprehensive prompt for Gemini"""
        
        symptoms_text = ""
        if symptoms:
            symptoms_text = f"\n\nDetected Symptoms:\n{json.dumps(symptoms, indent=2)}"
        
        history_text = ""
        if medical_history:
            history_text = f"\n\nMedical History:\n{medical_history}"
        
        prompt = f"""
You are an expert neurologist and lifestyle medicine specialist. Generate comprehensive, personalized lifestyle recommendations for a patient with the following profile:

**Patient Profile:**
- Diagnosis: {diagnosis}
- Parkinson's Disease Probability: {pd_probability:.1f}%
- AI Confidence Level: {confidence:.1f}%
- Age: {age} years{symptoms_text}{history_text}

**Task:**
Generate detailed, actionable lifestyle recommendations in the following categories:

1. **Exercise & Physical Activity**
   - Specific exercises recommended for Parkinson's (if applicable)
   - Frequency and duration guidelines
   - Safety precautions
   - Progressive difficulty levels

2. **Diet & Nutrition**
   - Recommended foods and nutrients
   - Foods to limit or avoid
   - Meal timing considerations
   - Hydration guidelines

3. **Mental Health & Cognitive Wellness**
   - Stress management techniques
   - Cognitive exercises
   - Social engagement recommendations
   - Mood monitoring strategies

4. **Sleep & Rest**
   - Sleep hygiene practices
   - Optimal sleep schedule
   - Managing sleep disturbances
   - Relaxation techniques

5. **Daily Living & Routine**
   - Morning routines
   - Activity scheduling
   - Energy conservation strategies
   - Home safety modifications (if applicable)

6. **Medical Management**
   - Regular monitoring recommendations
   - When to consult healthcare providers
   - Medication reminders (general)
   - Symptom tracking suggestions

7. **Technology & Support**
   - Helpful apps and devices
   - Support groups and communities
   - Caregiver resources (if applicable)

**Format Requirements:**
- Provide 3-5 specific, actionable recommendations per category
- Include WHY each recommendation is beneficial
- Prioritize evidence-based practices
- Use clear, compassionate language
- Consider the patient's age and diagnosis severity

Return your response as a valid JSON object with this structure:
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
        """Parse Gemini response into structured format"""
        try:
            # Try to extract JSON from response
            # Gemini sometimes wraps JSON in markdown code blocks
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
            
            # Validate structure
            required_keys = [
                'exercise', 'nutrition', 'mental_health', 
                'sleep', 'daily_living', 'medical_management', 'technology_support'
            ]
            
            for key in required_keys:
                if key not in recommendations:
                    recommendations[key] = []
            
            return recommendations
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            # Fallback: create structured response from text
            return self._create_fallback_structure(response_text)
    
    def _create_fallback_structure(self, text: str) -> Dict[str, Any]:
        """Create structured recommendations from unstructured text"""
        # Split by common headers
        categories = {
            'exercise': [],
            'nutrition': [],
            'mental_health': [],
            'sleep': [],
            'daily_living': [],
            'medical_management': [],
            'technology_support': []
        }
        
        # Simple parsing - add the full text as a single recommendation
        categories['general'] = [{
            'title': 'General Recommendations',
            'description': text,
            'benefits': 'AI-generated comprehensive guidance'
        }]
        
        return categories
    
    def _get_fallback_recommendations(self, diagnosis: str, age: int) -> Dict[str, Any]:
        """Provide fallback recommendations if AI generation fails"""
        
        is_pd = 'parkinson' in diagnosis.lower()
        
        recommendations = {
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
                },
                {
                    'title': 'Social Engagement',
                    'description': 'Maintain regular social connections with family and friends',
                    'frequency': 'Regular basis',
                    'benefits': 'Combats isolation and supports mental health'
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
        
        return recommendations


# Singleton instance
_gemini_service: Optional[GeminiLifestyleService] = None


def get_gemini_service() -> GeminiLifestyleService:
    """Get or create Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiLifestyleService()
    return _gemini_service
