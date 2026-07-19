"""
AI Service — Databricks Foundation Model API integration.

Provides LLM capabilities for triage, chat, and recommendation explanations.
Uses Databricks Foundation Model APIs (Llama, Mixtral, etc.)
"""

import os
import json
from typing import Optional, Dict, List, Generator
from dataclasses import dataclass

# Databricks Foundation Model API endpoints
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")

# Available models on Databricks
AVAILABLE_MODELS = {
    "llama-3.3-70b": "databricks-llama-3.3-70b-instruct",
    "llama-3.1-8b": "databricks-llama-3.1-8b-instruct",
    "mixtral-8x7b": "databricks-mixtral-8x7b-instruct",
    "mixtral-8x22b": "databricks-mixtral-8x22b-instruct",
}

DEFAULT_MODEL = "llama-3.3-70b"


@dataclass
class AIMessage:
    role: str  # "system", "user", "assistant"
    content: str


class AIService:
    def __init__(self):
        self.available = bool(DATABRICKS_HOST and DATABRICKS_TOKEN)
        if not self.available:
            print("[ai] Databricks credentials not configured. AI features disabled.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers for Databricks."""
        return {
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",
            "Content-Type": "application/json",
        }
    
    def _get_endpoint(self, model: str = DEFAULT_MODEL) -> str:
        """Get API endpoint for model."""
        model_id = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS[DEFAULT_MODEL])
        return f"{DATABRICKS_HOST}/serving-endpoints/{model_id}/invocations"
    
    def chat_completion(
        self,
        messages: List[AIMessage],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Optional[str]:
        """Get chat completion from Databricks."""
        if not self.available:
            return None
        
        try:
            import requests
            
            endpoint = self._get_endpoint(model)
            headers = self._get_headers()
            
            payload = {
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"[ai] Chat completion error: {e}")
            return None
    
    def triage_assessment(
        self,
        symptoms: str,
        patient_age: Optional[int] = None,
        patient_gender: Optional[str] = None
    ) -> Optional[Dict]:
        """Use LLM for enhanced triage assessment."""
        if not self.available:
            return None
        
        system_prompt = """You are a medical triage assistant. Analyze the patient's symptoms and provide:
1. Primary specialty recommendation (cardiology, orthopedics, etc.)
2. Urgency level (EMERGENT, URGENT, SEMI_URGENT, NON_URGENT, ROUTINE)
3. Key symptoms identified
4. Red flags if any
5. Recommended next steps

Respond in JSON format with these fields:
{
    "specialty": "string",
    "urgency": "string",
    "symptoms": ["list of symptoms"],
    "red_flags": ["list of red flags"],
    "recommendations": ["list of recommendations"],
    "confidence": 0.0-1.0
}

Important: This is for informational purposes only. Always recommend consulting a healthcare professional."""
        
        user_message = f"Patient symptoms: {symptoms}"
        if patient_age:
            user_message += f"\nPatient age: {patient_age}"
        if patient_gender:
            user_message += f"\nPatient gender: {patient_gender}"
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=user_message),
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        if response:
            try:
                # Extract JSON from response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw response
                return {"raw_response": response}
        
        return None
    
    def explain_recommendation(
        self,
        facility_name: str,
        trust_score: float,
        capabilities: List[str],
        patient_needs: str
    ) -> Optional[str]:
        """Generate human-readable explanation for hospital recommendation."""
        if not self.available:
            return None
        
        system_prompt = """You are a healthcare advisor. Explain why a hospital is recommended for a patient.
Be concise, clear, and focus on the most relevant factors. Use simple language.
Max 2-3 sentences."""
        
        user_message = f"""Explain why {facility_name} is recommended:
- Trust score: {trust_score}/100
- Capabilities: {', '.join(capabilities[:5])}
- Patient needs: {patient_needs}"""
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=user_message),
        ]
        
        return self.chat_completion(messages, temperature=0.5, max_tokens=200)
    
    def analyze_facility_quality(
        self,
        facility_data: Dict
    ) -> Optional[Dict]:
        """Use LLM to analyze facility quality from available data."""
        if not self.available:
            return None
        
        system_prompt = """Analyze healthcare facility quality based on available data.
Provide:
1. Overall quality assessment (Excellent, Good, Fair, Poor)
2. Key strengths
3. Areas for improvement
4. Confidence level

Respond in JSON format:
{
    "quality": "string",
    "strengths": ["list"],
    "improvements": ["list"],
    "confidence": 0.0-1.0
}"""
        
        # Prepare facility data for analysis
        facility_summary = {
            "name": facility_data.get("name"),
            "trust_score": facility_data.get("_trust_score"),
            "capabilities": facility_data.get("capability"),
            "doctors": facility_data.get("numberDoctors"),
            "capacity": facility_data.get("capacity"),
        }
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=f"Analyze this facility:\n{json.dumps(facility_summary, indent=2)}"),
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        if response:
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                return {"raw_response": response}
        
        return None
    
    def generate_health_insights(
        self,
        region_data: Dict,
        facility_data: List[Dict]
    ) -> Optional[Dict]:
        """Generate health insights for a region using LLM."""
        if not self.available:
            return None
        
        system_prompt = """Analyze healthcare data for a region and provide insights:
1. Key health challenges
2. Coverage gaps
3. Recommendations for improvement
4. Priority areas

Respond in JSON format:
{
    "challenges": ["list"],
    "gaps": ["list"],
    "recommendations": ["list"],
    "priorities": ["list"]
}"""
        
        # Summarize data for analysis
        summary = {
            "region": region_data,
            "facility_count": len(facility_data),
            "sample_facilities": facility_data[:3] if facility_data else [],
        }
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=f"Analyze this healthcare data:\n{json.dumps(summary, indent=2)}"),
        ]
        
        response = self.chat_completion(messages, temperature=0.5)
        
        if response:
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                return {"raw_response": response}
        
        return None


# Global AI service instance
ai_service = AIService()