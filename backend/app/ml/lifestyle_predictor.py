"""
Lifestyle Recommendation Prediction Service
Loads the trained model (12K dataset) and provides predictions based on user inputs.
Now includes parkinson_status and parkinson_stage as key input features.
"""

import os
import pickle
import json
import numpy as np
from typing import Optional, Dict, Any

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "lifestyle_model.pkl")
ENCODERS_PATH = os.path.join(MODEL_DIR, "lifestyle_encoders.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "lifestyle_model_metadata.json")


class LifestylePredictor:
    """Predicts lifestyle recommendations based on user profile + Parkinson's data."""

    def __init__(self):
        self.model = None
        self.encoders = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        """Load trained model, encoders, and metadata."""
        try:
            if not os.path.exists(MODEL_PATH):
                print(f" Lifestyle model not found at {MODEL_PATH}")
                return

            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)

            with open(ENCODERS_PATH, "rb") as f:
                self.encoders = pickle.load(f)

            with open(METADATA_PATH, "r") as f:
                self.metadata = json.load(f)

            print(" Lifestyle recommendation model loaded (12K dataset)")
        except Exception as e:
            print(f" Error loading lifestyle model: {e}")
            self.model = None

    def is_ready(self) -> bool:
        return self.model is not None and self.encoders is not None

    def _create_age_group(self, age: int) -> str:
        if age < 45:
            return "young"
        elif age < 55:
            return "middle"
        elif age < 65:
            return "senior"
        elif age < 75:
            return "elderly"
        else:
            return "very_elderly"

    def _safe_encode(self, encoder_name: str, value: str) -> int:
        encoder = self.encoders.get(encoder_name)
        if encoder is None:
            return 0
        value = str(value).strip()
        if value in encoder.classes_:
            return int(encoder.transform([value])[0])
        lower_map = {c.lower(): c for c in encoder.classes_}
        if value.lower() in lower_map:
            return int(encoder.transform([lower_map[value.lower()]])[0])
        print(f" Unknown value '{value}' for {encoder_name}, using default '{encoder.classes_[0]}'")
        return 0

    def _extract_location(self, address: str) -> Dict[str, str]:
        """Extract city and state from address string."""
        address = str(address).strip()
        
        known_cities = {
            "bangalore": "Bangalore", "bengaluru": "Bangalore",
            "chennai": "Chennai", "madras": "Chennai",
            "coimbatore": "Coimbatore", "kovai": "Coimbatore",
            "erode": "Erode",
            "hyderabad": "Hyderabad",
            "karur": "Karur",
            "madurai": "Madurai",
            "mumbai": "Mumbai", "bombay": "Mumbai",
            "salem": "Salem",
        }
        known_states = {
            "tn": "TN", "tamil nadu": "TN", "tamilnadu": "TN",
            "ka": "KA", "karnataka": "KA",
            "ts": "TS", "telangana": "TS",
            "mh": "MH", "maharashtra": "MH",
        }

        city = "Chennai"
        state = "TN"
        address_lower = address.lower()
        
        for key, val in known_cities.items():
            if key in address_lower:
                city = val
                break
        for key, val in known_states.items():
            if key in address_lower:
                state = val
                break
        
        # Parse space-separated "City STATE Country" format
        parts = address.split()
        if len(parts) >= 1:
            first_word = parts[0].strip(",")
            for key, val in known_cities.items():
                if first_word.lower() == key:
                    city = val
                    break
            if len(parts) >= 2:
                second_word = parts[1].strip(",")
                for key, val in known_states.items():
                    if second_word.lower() == key:
                        state = val
                        break

        return {"city": city, "state": state}

    def predict(
        self,
        gender: str,
        age: int,
        address: str,
        previous_condition: str,
        parkinson_status: int = 0,
        parkinson_stage: int = 0,
    ) -> Dict[str, Any]:
        """
        Predict lifestyle recommendations.
        
        Args:
            gender: 'Male' or 'Female'
            age: User's age
            address: Location string
            previous_condition: Health condition
            parkinson_status: 0 = No Parkinson, 1 = Has Parkinson
            parkinson_stage: 0-3 (0=healthy, 1=early, 2=moderate, 3=advanced)
        """
        if not self.is_ready():
            return self._get_fallback(gender, age, previous_condition, parkinson_status, parkinson_stage)

        try:
            gender_norm = "Male" if gender.lower().startswith("m") else "Female"
            age_group = self._create_age_group(age)
            location = self._extract_location(address)

            # Normalize condition
            condition_map = {
                "none": "None",
                "diabetes": "Diabetes",
                "hypertension": "Hypertension",
                "heart disease": "Heart Disease",
                "arthritis": "Arthritis",
                "joint pain": "Arthritis",
                "obesity": "Obesity",
                "hypertension + diabetes": "Hypertension + Diabetes",
                "hypertension and diabetes": "Hypertension + Diabetes",
                "both hypertension and diabetes": "Hypertension + Diabetes",
                "diabetes and hypertension": "Hypertension + Diabetes",
            }
            condition_norm = condition_map.get(
                previous_condition.lower().strip(), previous_condition.strip()
            )

            # Clamp parkinson values
            parkinson_status = max(0, min(1, int(parkinson_status)))
            parkinson_stage = max(0, min(3, int(parkinson_stage)))
            
            # If status is 0, stage must be 0
            if parkinson_status == 0:
                parkinson_stage = 0

            # Feature vector: [gender, age_group, city, state, previous_condition, age, parkinson_status, parkinson_stage]
            encoded_features = [
                self._safe_encode("gender", gender_norm),
                self._safe_encode("age_group", age_group),
                self._safe_encode("city", location["city"]),
                self._safe_encode("state", location["state"]),
                self._safe_encode("previous_condition", condition_norm),
                age,
                parkinson_status,
                parkinson_stage,
            ]

            X = np.array([encoded_features])
            y_pred = self.model.predict(X)

            target_columns = self.metadata["target_columns"]
            raw_results = {}
            for i, col in enumerate(target_columns):
                encoder = self.encoders[col]
                raw_results[col] = encoder.inverse_transform([int(y_pred[0][i])])[0]

            # Get parkinson label
            stage_labels = self.metadata.get("parkinson_labels", {}).get("parkinson_stage", {})
            stage_label = stage_labels.get(str(parkinson_stage), f"Stage {parkinson_stage}")

            return {
                "success": True,
                "source": "ml_model",
                "input": {
                    "gender": gender_norm,
                    "age": age,
                    "age_group": age_group,
                    "location": location,
                    "previous_condition": condition_norm,
                    "parkinson_status": parkinson_status,
                    "parkinson_stage": parkinson_stage,
                    "parkinson_stage_label": stage_label,
                },
                "recommendations": {
                    "exercise": {
                        "category": "Exercise & Physical Activity",
                        "recommendation": raw_results["recommended_exercise"],
                        "details": self._exercise_details(raw_results["recommended_exercise"], parkinson_stage),
                        "priority": "high"
                    },
                    "diet": {
                        "category": "Nutrition & Diet",
                        "recommendation": raw_results["recommended_diet"],
                        "details": self._diet_details(raw_results["recommended_diet"], condition_norm),
                        "priority": "high"
                    },
                    "sleep": {
                        "category": "Sleep & Rest",
                        "recommendation": raw_results["recommended_sleep"],
                        "details": self._sleep_details(raw_results["recommended_sleep"], parkinson_stage),
                        "priority": "medium" if parkinson_stage < 2 else "high"
                    },
                    "stress_management": {
                        "category": "Stress Management & Wellbeing",
                        "recommendation": raw_results["recommended_stress_management"],
                        "details": self._stress_details(raw_results["recommended_stress_management"], parkinson_stage),
                        "priority": "medium"
                    }
                },
                "model_accuracy": self.metadata.get("overall_accuracy", 0),
            }

        except Exception as e:
            print(f" Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback(gender, age, previous_condition, parkinson_status, parkinson_stage)

    # ========== Detailed tip generators ==========

    def _exercise_details(self, rec: str, stage: int) -> list:
        base = {
            "Regular Exercise 4-5 days/week": [
                "Aim for 30-45 minutes of moderate exercise 4-5 days per week",
                "Include brisk walking, cycling, or swimming",
                "Add bodyweight exercises like squats, lunges, and push-ups",
                "Warm up for 5-10 minutes before and cool down after each session",
                "Track your progress and gradually increase intensity",
            ],
            "Moderate Cardio + Flexibility": [
                "Start with 20-30 minutes of moderate-intensity cardio (walking, cycling)",
                "Include daily stretching or yoga for flexibility",
                "Focus on hip, shoulder, and spine mobility exercises",
                "Consider tai chi for balance improvement and relaxation",
                "Exercise at the same time each day to build a routine",
            ],
            "Balance Training + Light Strength Work": [
                "Practice standing on one leg for 30 seconds, 3-4 times each side",
                "Use resistance bands for gentle strength training",
                "Include heel-to-toe walks to improve balance",
                "Add light dumbbell exercises (1-3 kg) for upper body strength",
                "Practice sit-to-stand exercises to maintain leg strength",
            ],
            "Assisted Physiotherapy + Fall Prevention": [
                "Work with a physiotherapist to design a safe exercise plan",
                "Focus on chair-based exercises for stability",
                "Practice controlled movements with a support bar or railing",
                "Wear non-slip footwear during all exercises",
                "Have a caregiver present during balance exercises",
            ],
            "Customized Activity Plan": [
                "Consult your neurologist and physiotherapist for a personalized plan",
                "Follow prescribed therapeutic exercises daily",
                "Include gentle range-of-motion exercises for stiff joints",
                "Use adaptive equipment if needed for safety",
                "Monitor fatigue levels and rest as needed between activities",
            ],
        }
        tips = base.get(rec, ["Follow the recommended exercise routine consistently"])
        if stage >= 2:
            tips.append("⚠️ Always exercise under supervision due to fall risk")
        return tips

    def _diet_details(self, rec: str, condition: str) -> list:
        base = {
            "Balanced Whole Food Diet": [
                "Eat a variety of fruits, vegetables, whole grains, and lean proteins",
                "Choose minimally processed foods over packaged items",
                "Include healthy fats from nuts, seeds, and olive oil",
                "Drink at least 8 glasses of water daily",
                "Eat regular meals at consistent times",
            ],
            "Low Sodium DASH Diet": [
                "Limit daily sodium intake to less than 2,300 mg",
                "Eat 4-5 servings of fruits and vegetables daily",
                "Choose whole grains over refined grains",
                "Use herbs and spices instead of salt for flavor",
                "Avoid processed meats, canned soups, and salty snacks",
            ],
            "Low Sugar High Fiber Diet": [
                "Limit refined sugars and sweetened beverages",
                "Include high-fiber foods: oats, legumes, whole grains, vegetables",
                "Choose low-glycemic fruits like berries, apples, and pears",
                "Monitor blood glucose levels regularly",
                "Eat protein with each meal to stabilize blood sugar",
            ],
            "Low Cholesterol Heart Diet": [
                "Reduce saturated fat — avoid fried foods and fatty meats",
                "Choose lean proteins: fish, chicken, beans, tofu",
                "Include soluble fiber from oats, barley, and fruits",
                "Use olive oil or canola oil instead of butter",
                "Eat fatty fish (salmon, mackerel) 2-3 times per week for omega-3s",
            ],
            "Mediterranean + Omega-3 Diet": [
                "Base meals on vegetables, fruits, whole grains, and legumes",
                "Include fatty fish rich in omega-3s (salmon, sardines) 2-3 times/week",
                "Use extra virgin olive oil as your primary cooking fat",
                "Include walnuts, flaxseeds, and chia seeds for plant-based omega-3s",
                "Limit red meat, sugar, and processed foods",
            ],
        }
        tips = base.get(rec, ["Follow the recommended dietary guidelines"])
        if "Diabetes" in condition:
            tips.append("📊 Monitor carbohydrate intake and blood sugar before/after meals")
        return tips

    def _sleep_details(self, rec: str, stage: int) -> list:
        base = {
            "6-8 Hours Healthy Sleep": [
                "Maintain a consistent sleep and wake schedule",
                "Create a dark, cool, and quiet bedroom environment",
                "Avoid screens (phone, TV) at least 30 minutes before bed",
                "Limit caffeine intake after 2 PM",
                "Include light physical activity during the day to improve sleep quality",
            ],
            "7-8 Hours Consistent Sleep": [
                "Set a fixed bedtime and wake-up time, even on weekends",
                "Develop a relaxing pre-sleep routine (warm bath, reading, music)",
                "Keep your bedroom cool (18-21°C / 65-70°F)",
                "Avoid heavy meals and alcohol close to bedtime",
                "Use blackout curtains to block light",
            ],
            "8 Hours Fixed Sleep Routine": [
                "Aim for a full 8 hours of uninterrupted sleep each night",
                "Take a warm bath before bed to promote relaxation",
                "Use a firm, comfortable mattress and supportive pillows",
                "Consider a satin pillowcase to ease turning in bed",
                "Keep a dim nightlight for safe nighttime bathroom trips",
            ],
        }
        tips = base.get(rec, ["Maintain a consistent sleep schedule"])
        if stage >= 2:
            tips.append("🛏️ Use bed rails or guardrails for safety during sleep")
        return tips

    def _stress_details(self, rec: str, stage: int) -> list:
        base = {
            "Guided Meditation + Breathing Therapy": [
                "Practice 10-15 minutes of guided meditation daily (apps: Headspace, Calm)",
                "Try the 4-7-8 breathing technique: inhale 4s, hold 7s, exhale 8s",
                "Practice progressive muscle relaxation before bed",
                "Keep a gratitude journal — write 3 things you're thankful for daily",
                "Join a support group to share experiences and reduce isolation",
            ],
            "Yoga + Outdoor Relaxation": [
                "Practice gentle yoga poses 2-3 times per week (chair yoga if needed)",
                "Spend at least 20-30 minutes outdoors in nature daily",
                "Try gardening as a therapeutic and calming activity",
                "Practice deep breathing during outdoor walks",
                "Listen to calming music or nature sounds for relaxation",
            ],
        }
        tips = base.get(rec, ["Practice regular stress management activities"])
        if stage >= 1:
            tips.append("💬 Consider speaking with a counselor specializing in chronic illness support")
        return tips

    def _get_fallback(self, gender, age, condition, pd_status, pd_stage) -> Dict[str, Any]:
        return {
            "success": True,
            "source": "fallback",
            "input": {
                "gender": gender, "age": age, "previous_condition": condition,
                "parkinson_status": pd_status, "parkinson_stage": pd_stage,
                "parkinson_stage_label": ["Healthy", "Early Stage", "Moderate Stage", "Advanced Stage"][min(pd_stage, 3)]
            },
            "recommendations": {
                "exercise": {
                    "category": "Exercise & Physical Activity",
                    "recommendation": "Moderate Walking 30 mins daily",
                    "details": ["Start with 15-20 minutes and gradually increase", "Include stretching exercises"],
                    "priority": "high"
                },
                "diet": {
                    "category": "Nutrition & Diet",
                    "recommendation": "Balanced Whole Food Diet",
                    "details": ["Focus on whole grains, fruits, and vegetables", "Limit processed foods"],
                    "priority": "high"
                },
                "sleep": {
                    "category": "Sleep & Rest",
                    "recommendation": "7-8 Hours Consistent Sleep",
                    "details": ["Maintain consistent sleep and wake times"],
                    "priority": "medium"
                },
                "stress_management": {
                    "category": "Stress Management & Wellbeing",
                    "recommendation": "Guided Meditation + Breathing Therapy",
                    "details": ["Practice 10-15 minutes of meditation daily"],
                    "priority": "medium"
                }
            },
            "model_accuracy": 0
        }

    def get_available_conditions(self) -> list:
        if self.metadata:
            conditions = self.metadata.get("unique_values", {}).get("previous_condition", [])
            return [c for c in conditions if c != "None"]
        return ["Diabetes", "Hypertension", "Heart Disease", "Arthritis", "Obesity", "Hypertension + Diabetes"]


# Singleton
_predictor = None

def get_lifestyle_predictor() -> LifestylePredictor:
    global _predictor
    if _predictor is None:
        _predictor = LifestylePredictor()
    return _predictor
