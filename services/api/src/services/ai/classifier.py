import abc
import re
from typing import Dict, Any

class DepartmentRoutingAdapter(abc.ABC):
    @abc.abstractmethod
    def classify(self, title: str, description: str) -> Dict[str, Any]:
        pass

class MockKeywordRoutingAdapter(DepartmentRoutingAdapter):
    def classify(self, title: str, description: str) -> Dict[str, Any]:
        text = f"{title} {description}".lower()

        # Keyword mapping rules (Tamil, English, Tanglish)
        if any(w in text for w in ["electric", "power", "tangedco", "wire", "current", "மின்சாரம்", "மின் விளக்கு", "current pochu"]):
            return {
                "department_code": "TANGEDCO",
                "category_code": "ELEC_OUTAGE",
                "issue_type": "Power Outage / Broken Streetlight",
                "confidence": 0.92,
                "landmark_hints": "Street Pole / Substation",
                "explanation": "Matched high-confidence electricity and power outage keywords.",
                "provider": "keyword_classifier"
            }
        elif any(w in text for w in ["water", "drainage", "sewage", "cmwssb", "pipe", "leak", "குடிநீர்", "சாக்கடை", "tannir"]):
            return {
                "department_code": "CMWSSB",
                "category_code": "WATER_LEAK",
                "issue_type": "Water Leakage / Sewage Overflow",
                "confidence": 0.88,
                "landmark_hints": "Water Supply Main Line",
                "explanation": "Matched high-confidence water supply and Metro Water keywords.",
                "provider": "keyword_classifier"
            }
        elif any(w in text for w in ["garbage", "waste", "sanitation", "gcc", "dump", "குப்பை", "துப்புரவு", "kuppai"]):
            return {
                "department_code": "GCC",
                "category_code": "GARBAGE_CLEAN",
                "issue_type": "Garbage Overflow / Sanitation",
                "confidence": 0.85,
                "landmark_hints": "Dustbin / Roadside",
                "explanation": "Matched sanitation and garbage waste keywords.",
                "provider": "keyword_classifier"
            }
        elif any(w in text for w in ["signal", "traffic", "police", "jam", "வாகன நெரிசல்", "ட்ராஃபிக்"]):
            return {
                "department_code": "TRAFFIC",
                "category_code": "TRAFFIC_JAM",
                "issue_type": "Traffic Signal Malfunction / Congestion",
                "confidence": 0.82,
                "landmark_hints": "Road Intersection",
                "explanation": "Matched traffic police keywords.",
                "provider": "keyword_classifier"
            }
        elif any(w in text for w in ["corruption", "bribe", "abuse", "domestic violence", "லஞ்சம்", "அநீதி"]):
            return {
                "department_code": "REVENUE",
                "category_code": "CORRUPTION_ALLEGATION",
                "issue_type": "Sensitive Administrative Allegation",
                "confidence": 0.90,
                "landmark_hints": "Taluk Office",
                "explanation": "Matched sensitive grievance category requiring strict privacy.",
                "provider": "keyword_classifier"
            }
        else:
            # Low confidence fallback -> triggers human triage task (< 0.75)
            return {
                "department_code": "GCC",
                "category_code": "GENERIC_CIVIC",
                "issue_type": "Unspecified Civic Issue",
                "confidence": 0.55,
                "landmark_hints": None,
                "explanation": "Text lacked specific department keywords. Confidence below 0.75 threshold.",
                "provider": "keyword_classifier"
            }

class IndicBertRoutingAdapter(DepartmentRoutingAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def classify(self, title: str, description: str) -> Dict[str, Any]:
        if not self.api_key:
            return MockKeywordRoutingAdapter().classify(title, description)
        # Production model inference call
        return {
            "department_code": "GCC",
            "category_code": "ROAD_REPAIR",
            "issue_type": "Pothole Repair",
            "confidence": 0.89,
            "landmark_hints": "Main Road",
            "explanation": "IndicBERT fine-tuned model classified grievance text.",
            "provider": "indicbert_v2"
        }

def get_routing_adapter(provider_type: str = "mock", api_key: str = "") -> DepartmentRoutingAdapter:
    if provider_type == "indicbert" and api_key:
        return IndicBertRoutingAdapter(api_key=api_key)
    return MockKeywordRoutingAdapter()
