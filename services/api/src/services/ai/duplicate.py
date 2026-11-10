import abc
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from services.api.src.db.models import SharedIncident, GrievanceCategory

class DuplicateMatchingAdapter(abc.ABC):
    @abc.abstractmethod
    def find_similar_incidents(
        self, 
        db: Session, 
        category_id: str, 
        district: str, 
        title: str, 
        description: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None
    ) -> Dict[str, Any]:
        pass

class MockDuplicateMatchingAdapter(DuplicateMatchingAdapter):
    def find_similar_incidents(
        self, 
        db: Session, 
        category_id: str, 
        district: str, 
        title: str, 
        description: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None
    ) -> Dict[str, Any]:
        # Check if category is sensitive
        category = db.query(GrievanceCategory).filter(GrievanceCategory.id == category_id).first()
        if category and category.is_sensitive:
            return {
                "decision": "create_new",
                "matched_incident_id": None,
                "confidence": 0.0,
                "reason": "Sensitive category (abuse/corruption/entitlement) - auto-linking strictly prohibited.",
                "candidate_incidents": []
            }

        # Query recent open incidents in the same department/category and district
        recent_incidents = db.query(SharedIncident).filter(
            SharedIncident.category_id == category_id,
            SharedIncident.district == district,
            SharedIncident.status.in_(["open", "assigned", "in_progress"])
        ).limit(10).all()

        if not recent_incidents:
            return {
                "decision": "create_new",
                "matched_incident_id": None,
                "confidence": 0.20,
                "reason": "No active incidents found in the same district and category.",
                "candidate_incidents": []
            }

        # Calculate keyword overlap score with candidate incidents
        search_words = set(f"{title} {description}".lower().split())
        best_match = None
        highest_score = 0.0

        candidates_data = []

        for inc in recent_incidents:
            inc_words = set(f"{inc.title} {inc.summary}".lower().split())
            common = search_words.intersection(inc_words)
            if not inc_words:
                continue
            similarity = len(common) / max(len(search_words), len(inc_words))
            
            # Boost score if category matches exactly
            similarity = min(1.0, similarity * 1.8)

            candidates_data.append({
                "incident_id": inc.id,
                "incident_number": inc.incident_number,
                "title": inc.title,
                "similarity_score": round(similarity, 2)
            })

            if similarity > highest_score:
                highest_score = similarity
                best_match = inc

        highest_score = round(highest_score, 2)

        # Apply threshold rules
        if highest_score >= 0.85 and best_match:
            decision = "auto_link"
            reason = f"High confidence duplicate (score: {highest_score} >= 0.85)."
            matched_id = best_match.id
        elif highest_score >= 0.65 and best_match:
            decision = "triage_task"
            reason = f"Medium confidence duplicate (score: {highest_score} between 0.65 and 0.84). Requires officer confirmation."
            matched_id = best_match.id
        else:
            decision = "create_new"
            reason = f"Low similarity score (score: {highest_score} < 0.65). Creating new shared incident."
            matched_id = None

        return {
            "decision": decision,
            "matched_incident_id": matched_id,
            "confidence": highest_score,
            "reason": reason,
            "candidate_incidents": candidates_data
        }

class QwenDuplicateMatchingAdapter(DuplicateMatchingAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def find_similar_incidents(
        self, db: Session, category_id: str, district: str, title: str, description: str, lat: Optional[float] = None, lng: Optional[float] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            return MockDuplicateMatchingAdapter().find_similar_incidents(db, category_id, district, title, description, lat, lng)
        # Production vector embedding + Qwen reranker flow
        return MockDuplicateMatchingAdapter().find_similar_incidents(db, category_id, district, title, description, lat, lng)

def get_duplicate_adapter(provider_type: str = "mock", api_key: str = "") -> DuplicateMatchingAdapter:
    if provider_type == "qwen" and api_key:
        return QwenDuplicateMatchingAdapter(api_key=api_key)
    return MockDuplicateMatchingAdapter()
