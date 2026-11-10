from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from services.api.src.db.models import SharedIncident, PriorityAssessment, PriorityOverride, AuditEvent, now_utc

LIFE_SAFETY_KEYWORDS = [
    "fire", "electrical wire", "live wire", "open manhole", "severe flooding", 
    "building collapse", "gas leak", "தீ", "மின் கம்பி", "சாக்கடை மூடி திறந்தது", "வெள்ளம்"
]

CRITICAL_LOCATION_KEYWORDS = [
    "hospital", "school", "bus stand", "railway station", "transit hub", "அரசு மருத்துவமனை", "பள்ளி"
]

def calculate_priority_score(
    title: str,
    summary: str,
    distinct_reporters_count: int = 1,
    landmark_location: Optional[str] = None,
    is_sla_at_risk: bool = False,
    historical_recurrence_count: int = 0
) -> Dict[str, Any]:
    text = f"{title} {summary}".lower()

    # 1. Life Safety Check (Immediate High Priority rule)
    is_life_safety = any(k in text for k in LIFE_SAFETY_KEYWORDS)
    if is_life_safety:
        safety_severity = 40.0
        public_impact = min(25.0, distinct_reporters_count * 5.0)
        critical_location = 15.0 if landmark_location and any(k in landmark_location.lower() for k in CRITICAL_LOCATION_KEYWORDS) else 10.0
        sla_risk = 10.0 if is_sla_at_risk else 5.0
        recurrence = min(10.0, historical_recurrence_count * 2.0)
        
        total_score = min(100.0, safety_severity + public_impact + critical_location + sla_risk + recurrence)
        # Ensure it falls into High priority (>= 70)
        total_score = max(85.0, total_score)
        
        return {
            "safety_severity": safety_severity,
            "verified_public_impact": public_impact,
            "critical_location": critical_location,
            "sla_risk": sla_risk,
            "recurrence": recurrence,
            "total_score": total_score,
            "priority_level": "high",
            "is_life_safety_override": True,
            "explanation": "Immediate HIGH priority assigned due to life-safety hazard detection (fire/wire/manhole/flooding)."
        }

    # Standard Explainable Calculation
    # Safety Severity: 0-40
    if any(k in text for k in ["hazard", "accident", "danger", "overflow", "அபாயம்"]):
        safety_severity = 25.0
    elif any(k in text for k in ["delay", "inconvenience", "blockage", "தாமதம்"]):
        safety_severity = 15.0
    else:
        safety_severity = 5.0

    # Verified Public Impact: 0-25 (count distinct verified reporters)
    public_impact = min(25.0, distinct_reporters_count * 5.0)

    # Critical Location: 0-15
    critical_location = 0.0
    if landmark_location and any(k in landmark_location.lower() for k in CRITICAL_LOCATION_KEYWORDS):
        critical_location = 15.0
    elif any(k in text for k in CRITICAL_LOCATION_KEYWORDS):
        critical_location = 10.0

    # SLA Risk: 0-10
    sla_risk = 10.0 if is_sla_at_risk else 2.0

    # Recurrence: 0-10
    recurrence = min(10.0, historical_recurrence_count * 2.5)

    total_score = round(safety_severity + public_impact + critical_location + sla_risk + recurrence, 1)

    if total_score >= 70.0:
        priority_level = "high"
    elif total_score >= 40.0:
        priority_level = "medium"
    else:
        priority_level = "low"

    return {
        "safety_severity": safety_severity,
        "verified_public_impact": public_impact,
        "critical_location": critical_location,
        "sla_risk": sla_risk,
        "recurrence": recurrence,
        "total_score": total_score,
        "priority_level": priority_level,
        "is_life_safety_override": False,
        "explanation": f"Score breakdown: Safety={safety_severity}, Impact={public_impact}, Location={critical_location}, SLA={sla_risk}, Recurrence={recurrence}."
    }

def record_priority_override(
    db: Session,
    incident_id: str,
    officer_id: str,
    new_priority: str,
    reason: str
) -> PriorityOverride:
    incident = db.query(SharedIncident).filter(SharedIncident.id == incident_id).first()
    if not incident:
        raise ValueError("Shared Incident not found")

    old_priority = incident.priority_level
    incident.priority_level = new_priority
    if new_priority == "high":
        incident.priority_score = max(75.0, incident.priority_score)
    elif new_priority == "medium":
        incident.priority_score = 50.0
    else:
        incident.priority_score = 25.0

    override_record = PriorityOverride(
        incident_id=incident_id,
        officer_id=officer_id,
        previous_priority=old_priority,
        new_priority=new_priority,
        reason=reason
    )
    db.add(override_record)

    # Save to audit log
    audit = AuditEvent(
        user_id=officer_id,
        user_role="officer",
        action="PRIORITY_OVERRIDDEN",
        target_entity="shared_incidents",
        target_id=incident_id,
        details={
            "previous_priority": old_priority,
            "new_priority": new_priority,
            "mandatory_reason": reason
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(override_record)
    return override_record
