from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.api.src.db.session import get_db
from services.api.src.db.models import (
    SharedIncident, Assignment, OfficerAction, PriorityOverride, 
    Department, GrievanceCategory, User, AuditEvent, PetitionStatusHistory, now_utc
)
from services.api.src.schemas.schemas import (
    IncidentOut, IncidentUpdate, AssignCreate, ActionCreate, PriorityOverrideCreate
)
from services.api.src.core.security import get_current_user, require_roles, redact_pii_for_shared_view
from services.api.src.services.priority import record_priority_override

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentOut])
def list_incidents(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    department_id: Optional[str] = None,
    district: Optional[str] = None,
    sla_risk_only: bool = False,
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin", "auditor"])),
    db: Session = Depends(get_db)
):
    query = db.query(SharedIncident)
    if status:
        query = query.filter(SharedIncident.status == status)
    if priority:
        query = query.filter(SharedIncident.priority_level == priority)
    if department_id:
        query = query.filter(SharedIncident.department_id == department_id)
    if district:
        query = query.filter(SharedIncident.district == district)
    if sla_risk_only:
        query = query.filter(SharedIncident.is_sla_breached == True)

    incidents = query.order_by(SharedIncident.priority_score.desc(), SharedIncident.created_at.desc()).all()

    # Format result with linked petition count and names
    result = []
    for inc in incidents:
        dept = db.query(Department).filter(Department.id == inc.department_id).first()
        cat = db.query(GrievanceCategory).filter(GrievanceCategory.id == inc.category_id).first()
        
        inc_data = {
            "id": inc.id,
            "incident_number": inc.incident_number,
            "title": inc.title,
            "summary": inc.summary,
            "district": inc.district,
            "category_name": cat.name_en if cat else None,
            "department_name": dept.name_en if dept else None,
            "priority_score": inc.priority_score,
            "priority_level": inc.priority_level,
            "status": inc.status,
            "distinct_reporter_count": inc.distinct_reporter_count,
            "linked_petitions_count": len(inc.petitions),
            "sla_hours": inc.sla_hours,
            "sla_due_at": inc.sla_due_at,
            "is_sla_breached": inc.is_sla_breached,
            "created_at": inc.created_at
        }
        result.append(inc_data)

    return result

@router.get("/{incident_id}")
def get_incident_detail(
    incident_id: str,
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin", "auditor"])),
    db: Session = Depends(get_db)
):
    inc = db.query(SharedIncident).filter(SharedIncident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Shared incident not found")

    dept = db.query(Department).filter(Department.id == inc.department_id).first()
    cat = db.query(GrievanceCategory).filter(GrievanceCategory.id == inc.category_id).first()

    # Anonymized petition details
    petitions_summary = []
    for p in inc.petitions:
        petitions_summary.append({
            "petition_number": p.petition_number,
            "status": p.status,
            "landmark": p.landmark,
            "submitted_at": p.created_at,
            # PII Redacted
            "citizen_name": "Anonymized Citizen",
            "phone_number": "[REDACTED]"
        })

    actions = db.query(OfficerAction).filter(OfficerAction.incident_id == incident_id).order_by(OfficerAction.created_at.desc()).all()
    overrides = db.query(PriorityOverride).filter(PriorityOverride.incident_id == incident_id).order_by(PriorityOverride.created_at.desc()).all()

    return {
        "id": inc.id,
        "incident_number": inc.incident_number,
        "title": inc.title,
        "summary": inc.summary,
        "district": inc.district,
        "department_name": dept.name_en if dept else None,
        "category_name": cat.name_en if cat else None,
        "priority_score": inc.priority_score,
        "priority_level": inc.priority_level,
        "status": inc.status,
        "distinct_reporter_count": inc.distinct_reporter_count,
        "linked_petitions_count": len(inc.petitions),
        "petitions": petitions_summary,
        "officer_actions": [{"action_type": a.action_type, "notes": a.notes, "created_at": a.created_at} for a in actions],
        "priority_overrides": [{"previous": o.previous_priority, "new": o.new_priority, "reason": o.reason, "created_at": o.created_at} for o in overrides],
        "sla_due_at": inc.sla_due_at,
        "is_sla_breached": inc.is_sla_breached,
        "created_at": inc.created_at
    }

@router.patch("/{incident_id}")
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin"])),
    db: Session = Depends(get_db)
):
    inc = db.query(SharedIncident).filter(SharedIncident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if payload.status:
        inc.status = payload.status
        # Update linked petitions status
        for p in inc.petitions:
            p.status = payload.status
            h = PetitionStatusHistory(
                petition_id=p.id,
                from_status=p.status,
                to_status=payload.status,
                remarks=f"Shared incident updated to {payload.status} by officer.",
                changed_by=current_user.id
            )
            db.add(h)

    if payload.summary:
        inc.summary = payload.summary

    db.commit()
    return {"message": "Incident updated successfully", "status": inc.status}

@router.post("/{incident_id}/assign")
def assign_incident(
    incident_id: str,
    payload: AssignCreate,
    current_user: User = Depends(require_roles(["supervisor", "admin", "officer"])),
    db: Session = Depends(get_db)
):
    inc = db.query(SharedIncident).filter(SharedIncident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    assign = Assignment(
        incident_id=incident_id,
        assigned_to_user_id=payload.assigned_to_user_id,
        assigned_by_user_id=current_user.id,
        remarks=payload.remarks
    )
    inc.status = "assigned"
    db.add(assign)
    db.commit()
    return {"message": "Incident assigned successfully"}

@router.post("/{incident_id}/actions")
def log_officer_action(
    incident_id: str,
    payload: ActionCreate,
    current_user: User = Depends(require_roles(["officer", "supervisor"])),
    db: Session = Depends(get_db)
):
    inc = db.query(SharedIncident).filter(SharedIncident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    action = OfficerAction(
        incident_id=incident_id,
        officer_id=current_user.id,
        action_type=payload.action_type,
        notes=payload.notes,
        evidence_url=payload.evidence_url
    )
    db.add(action)

    if payload.action_type == "resolution":
        inc.status = "resolved"
        for p in inc.petitions:
            p.status = "resolved"
            h = PetitionStatusHistory(
                petition_id=p.id,
                from_status=p.status,
                to_status="resolved",
                remarks=f"Resolved by Officer: {payload.notes}",
                changed_by=current_user.id
            )
            db.add(h)

    db.commit()
    return {"message": "Action logged successfully"}

@router.post("/{incident_id}/priority-override")
def override_priority(
    incident_id: str,
    payload: PriorityOverrideCreate,
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin"])),
    db: Session = Depends(get_db)
):
    try:
        override = record_priority_override(
            db=db,
            incident_id=incident_id,
            officer_id=current_user.id,
            new_priority=payload.new_priority,
            reason=payload.reason
        )
        return {
            "message": f"Priority overridden to {payload.new_priority}",
            "reason_recorded": override.reason,
            "timestamp": override.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
