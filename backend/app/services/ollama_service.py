"""
Ollama Service — Interface to local Llama 3.2 via Ollama API.
Used for:
  1. Validating & refining ML-generated lifestyle recommendations
  2. Powering the patient chatbot
"""

import os
import json
import httpx
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")


async def _call_ollama(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    timeout: float = 120.0,
    force_json: bool = False,
) -> Optional[str]:
    """
    Send a prompt to the local Ollama Llama 3.2 and return the response text.
    Returns None if Ollama is unreachable or errors.
    """
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        
        if force_json:
            payload["format"] = "json"

        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        payload["messages"].append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama returned {response.status_code}: {response.text[:300]}")
                return None

    except httpx.ConnectError:
        logger.warning("Ollama is not running or unreachable at %s", OLLAMA_BASE_URL)
        return None
    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        return None


async def check_ollama_health() -> bool:
    """Check if Ollama is running and the model is available."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m["name"] for m in models]
                return OLLAMA_MODEL in model_names
    except Exception:
        pass
    return False


# ============================================================
# 1. RECOMMENDATION VALIDATOR
# ============================================================

async def validate_and_refine_recommendations(
    user_profile: Dict[str, Any],
    ml_recommendations: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Send user profile + ML-generated recommendations to Llama 3.2.
    Llama MUST correct any medically inappropriate recommendations.
    
    Returns the original recommendations if Ollama is unavailable.
    """
    age = user_profile.get("age", 50)
    condition = str(user_profile.get("previous_condition", "None")).lower()
    pd_stage = user_profile.get("parkinson_stage", 0)
    pd_status = user_profile.get("parkinson_status", 0)

    # Build conflict warnings to help Llama focus
    conflicts = []
    if age >= 75:
        conflicts.append(f"CRITICAL: Patient is {age} years old (very elderly). High-intensity exercise like jogging, swimming, cycling, squats, lunges, push-ups is DANGEROUS. Replace with gentle, seated, or assisted exercises only.")
    if age >= 85:
        conflicts.append(f"CRITICAL: Patient is {age} years old (extremely elderly). ANY vigorous activity risks injury. Only recommend very gentle movements, chair exercises, assisted walking.")
    if "arthritis" in condition or "joint" in condition:
        conflicts.append("CRITICAL: Patient has Arthritis/Joint Pain. Do NOT recommend high-impact activities (jogging, running, jumping, squats, lunges, push-ups). Replace with low-impact alternatives: gentle stretching, chair yoga, warm water therapy, range-of-motion exercises.")
    if "heart" in condition:
        conflicts.append("CRITICAL: Patient has Heart Disease. Limit vigorous cardio. Recommend light walking, gentle stretching, breathing exercises.")
    if "diabetes" in condition:
        conflicts.append("Must monitor blood sugar around exercise. Include pre/post meal timing guidance.")
    if "obesity" in condition:
        conflicts.append("Focus on sustainable, gradual activity increases. Avoid high-impact exercises that stress joints.")
    if pd_stage >= 2:
        conflicts.append(f"CRITICAL: Patient has Parkinson's Stage {pd_stage}. Exercise MUST be supervised. Focus on balance, fall prevention, physiotherapy.")
    if pd_stage >= 3:
        conflicts.append("CRITICAL: Advanced Parkinson's. Only assisted/supervised exercises. Fall risk is very high.")

    conflict_text = "\n".join(f"⚠️ {c}" for c in conflicts) if conflicts else "No major conflicts detected."

    system_prompt = (
        "You are a senior medical advisor reviewing AI-generated lifestyle recommendations for patient safety.\n\n"
        "YOUR TASK: Review the ML model's recommendations against the patient's actual health profile. "
        "If ANY recommendation is inappropriate, unsafe, or conflicts with the patient's conditions, "
        "you MUST REPLACE IT with a safe, appropriate alternative.\n\n"
        "RULES:\n"
        "1. DO NOT just add a note saying 'consider reducing intensity'. Actually CHANGE the recommendation text AND all the detail tips.\n"
        "2. For elderly patients (75+) with joint problems: NEVER recommend jogging, swimming, cycling, squats, lunges, push-ups, or anything high-impact.\n"
        "3. For very elderly patients (85+): ONLY recommend chair exercises, gentle stretching, assisted walking, range-of-motion movements.\n"
        "4. If you change ANYTHING, set corrections_made to true.\n"
        "5. Each category MUST have exactly 5 detail tips that are SPECIFIC and ACTIONABLE.\n"
        "6. The ai_note should explain WHY you changed (or kept) the recommendation.\n\n"
        "RESPOND IN VALID JSON ONLY. No other text before or after the JSON.\n"
        "{\n"
        '  "validated": true,\n'
        '  "corrections_made": true or false,\n'
        '  "recommendations": {\n'
        '    "exercise": {"recommendation": "CORRECTED title here", "details": ["tip1","tip2","tip3","tip4","tip5"], "ai_note": "Why changed/kept"},\n'
        '    "diet": {"recommendation": "CORRECTED title here", "details": ["tip1","tip2","tip3","tip4","tip5"], "ai_note": "Why changed/kept"},\n'
        '    "sleep": {"recommendation": "CORRECTED title here", "details": ["tip1","tip2","tip3","tip4","tip5"], "ai_note": "Why changed/kept"},\n'
        '    "stress_management": {"recommendation": "CORRECTED title here", "details": ["tip1","tip2","tip3","tip4","tip5"], "ai_note": "Why changed/kept"}\n'
        '  },\n'
        '  "general_advice": "Overall personalized advice paragraph for this patient"\n'
        "}"
    )

    # Build the user prompt with emphasis on known conflicts
    stage_labels = {
        0: "No Parkinson (healthy)",
        1: "Early Stage (mild symptoms)",
        2: "Moderate Stage",
        3: "Advanced Stage",
    }

    user_prompt = (
        f"## Patient Profile\n"
        f"- Gender: {user_profile.get('gender', 'Unknown')}\n"
        f"- Age: {age} years\n"
        f"- Location: {user_profile.get('location', 'Unknown')}\n"
        f"- Previous Health Condition: {user_profile.get('previous_condition', 'None')}\n"
        f"- Parkinson's Status: {'Has Parkinson' if pd_status == 1 else 'No Parkinson'}\n"
        f"- Parkinson's Stage: Stage {pd_stage} — {stage_labels.get(pd_stage, 'Unknown')}\n\n"
        f"## ⚠️ KNOWN CONFLICTS (must be addressed)\n{conflict_text}\n\n"
        f"## ML-Generated Recommendations to Review\n"
    )

    for category, rec_data in ml_recommendations.items():
        if isinstance(rec_data, dict):
            user_prompt += (
                f"\n### {rec_data.get('category', category)}\n"
                f"- Main Recommendation: {rec_data.get('recommendation', 'N/A')}\n"
                f"- Action Items:\n"
            )
            for detail in rec_data.get("details", []):
                user_prompt += f"  * {detail}\n"

    user_prompt += (
        "\n\n## YOUR TASK\n"
        "Review the above recommendations against the patient profile and conflicts. "
        "For EACH category: if the recommendation or any detail tip is unsafe or inappropriate "
        "for this patient, REPLACE the recommendation title and ALL detail tips with safe alternatives. "
        "Do NOT keep the original unsafe text. Respond in JSON ONLY."
    )

    response_text = await _call_ollama(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.2,  # Very low temperature for accurate medical review
        max_tokens=2000,
        timeout=300.0,
        force_json=True,
    )

    if not response_text:
        logger.warning("Ollama unavailable — returning original ML recommendations")
        return {
            "validated": False,
            "llama_available": False,
            "corrections_made": False,
            "recommendations": ml_recommendations,
            "general_advice": None,
        }

    # Parse the JSON response from Llama
    try:
        # Extract JSON from response (Llama may include markdown or extra text)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)

            # Merge Llama's refinements into the recommendation structure
            refined = {}
            llama_recs = parsed.get("recommendations", {})
            corrections_made = parsed.get("corrections_made", False)

            # If we detected conflicts, force corrections_made to True if Llama changed anything
            for key in ["exercise", "diet", "sleep", "stress_management"]:
                original = ml_recommendations.get(key, {})
                llama_rec = llama_recs.get(key, {})

                llama_main = llama_rec.get("recommendation", "")
                llama_details = llama_rec.get("details", [])

                # Use Llama's version if it provided one, otherwise keep original
                final_recommendation = llama_main if llama_main else original.get("recommendation", "")
                final_details = llama_details if llama_details else original.get("details", [])

                # Detect if Llama actually changed the recommendation
                if final_recommendation != original.get("recommendation", ""):
                    corrections_made = True

                refined[key] = {
                    "category": original.get("category", key),
                    "recommendation": final_recommendation,
                    "details": final_details,
                    "priority": original.get("priority", "medium"),
                    "ai_note": llama_rec.get("ai_note", ""),
                }

            return {
                "validated": True,
                "llama_available": True,
                "corrections_made": corrections_made,
                "recommendations": refined,
                "general_advice": parsed.get("general_advice", ""),
            }
        else:
            raise ValueError("No JSON found in response")

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse Llama response: {e}")
        logger.debug(f"Raw response: {response_text[:500]}")
        return {
            "validated": True,
            "llama_available": True,
            "corrections_made": False,
            "recommendations": ml_recommendations,
            "general_advice": response_text[:500],
        }


# ============================================================
# 2. CHATBOT
# ============================================================

async def chatbot_ask(
    message: str,
    user_name: str = "Patient",
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Handle a chatbot question using local Llama 3.2.
    Returns a helpful, professional response about health/Parkinson's.
    """
    system_prompt = (
        "You are a helpful, empathetic AI medical assistant named 'ParkinsonCare AI', "
        "assisting patients with questions about Parkinson's disease, general health, "
        "lifestyle, medications, and wellbeing.\n\n"
        "Guidelines:\n"
        "- Be warm, professional, and concise\n"
        "- DO NOT provide definitive medical diagnoses\n"
        "- Always recommend consulting a neurologist for specific medical decisions\n"
        "- Provide evidence-based information when possible\n"
        "- If the question is not health-related, politely guide the user back\n"
        "- Keep responses under 300 words unless the topic requires more detail\n"
        f"- The patient's name is {user_name}\n"
    )

    # Build conversation context if available
    if conversation_history and len(conversation_history) > 0:
        context = "\n\nPrevious conversation:\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context += f"{role.capitalize()}: {content}\n"
        message = context + f"\nPatient's new question: {message}"

    response = await _call_ollama(
        prompt=message,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=1024,
        timeout=60.0,
    )

    if response:
        return response
    else:
        return (
            "I'm sorry, I'm having trouble connecting to my AI engine right now. "
            "Please try again in a moment. If the issue persists, please ensure "
            "that the Ollama service is running on your system."
        )
