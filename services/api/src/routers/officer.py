from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.api.src.db.session import get_db
from services.api.src.db.models import (
    SharedIncident, TriageTask, Petition, Department, GrievanceCategory, User, AuditEvent, now_utc
)
from services.api.src.schemas.schemas import TriageTaskOut, TriageResolve
from services.api.src.core.security import get_current_user, require_roles
from services.api.src.services.priority import calculate_priority_score

router = APIRouter(tags=["Officer & Triage"])

@router.get("/officer/queue")
def get_officer_queue(
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin", "operator"])),
    db: Session = Depends(get_db)
):
    open_count = db.query(SharedIncident).filter(SharedIncident.status.in_(["open", "assigned", "in_progress"])).count()
    high_priority_count = db.query(SharedIncident).filter(
        SharedIncident.status.in_(["open", "assigned", "in_progress"]),
        SharedIncident.priority_level == "high"
    ).count()
    sla_at_risk_count = db.query(SharedIncident).filter(
        SharedIncident.status.in_(["open", "assigned", "in_progress"]),
        SharedIncident.is_sla_breached == True
    ).count()

    incidents = db.query(SharedIncident).filter(
        SharedIncident.status.in_(["open", "assigned", "in_progress"])
    ).order_by(SharedIncident.priority_score.desc()).limit(20).all()

    queue_data = []
    for inc in incidents:
        dept = db.query(Department).filter(Department.id == inc.department_id).first()
        cat = db.query(GrievanceCategory).filter(GrievanceCategory.id == inc.category_id).first()
        queue_data.append({
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
            "linked_petitions_count": len(inc.petitions),
            "sla_due_at": inc.sla_due_at,
            "is_sla_breached": inc.is_sla_breached,
            "created_at": inc.created_at
        })

    return {
        "metrics": {
            "open_incidents": open_count,
            "high_priority_incidents": high_priority_count,
            "sla_at_risk_incidents": sla_at_risk_count
        },
        "queue": queue_data
    }

@router.get("/triage/tasks", response_model=List[TriageTaskOut])
def list_triage_tasks(
    status: Optional[str] = "pending",
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin"])),
    db: Session = Depends(get_db)
):
    tasks = db.query(TriageTask).filter(TriageTask.status == status).order_by(TriageTask.created_at.desc()).all()
    
    result = []
    for t in tasks:
        p = db.query(Petition).filter(Petition.id == t.petition_id).first()
        result.append({
            "id": t.id,
            "task_type": t.task_type,
            "petition_id": t.petition_id,
            "petition_title": p.title if p else "Unknown Petition",
            "candidate_incident_id": t.candidate_incident_id,
            "confidence_score": t.confidence_score,
            "status": t.status,
            "created_at": t.created_at
        })
    return result

@router.post("/triage/tasks/{task_id}/resolve")
def resolve_triage_task(
    task_id: str,
    payload: TriageResolve,
    current_user: User = Depends(require_roles(["officer", "supervisor", "admin"])),
    db: Session = Depends(get_db)
):
    task = db.query(TriageTask).filter(TriageTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Triage task not found")

    petition = db.query(Petition).filter(Petition.id == task.petition_id).first()
    if not petition:
        raise HTTPException(status_code=404, detail="Associated petition not found")

    if payload.action == "link" and payload.target_incident_id:
        incident = db.query(SharedIncident).filter(SharedIncident.id == payload.target_incident_id).first()
        if incident:
            petition.shared_incident_id = incident.id
            petition.status = "linked"
            incident.distinct_reporter_count += 1
            task.resolution_action = "linked"

    elif payload.action == "create_new":
        dept_id = payload.target_department_id or task.suggested_department_id
        if not dept_id:
            dept = db.query(Department).first()
            dept_id = dept.id if dept else None

        cat = db.query(GrievanceCategory).first()
        p_res = calculate_priority_score(title=petition.title, summary=petition.description)

        new_inc = SharedIncident(
            incident_number=f"INC-TRIAGE-{petition.petition_number[-6:]}",
            category_id=cat.id if cat else "",
            department_id=dept_id,
            title=petition.title,
            summary=petition.description,
            district=petition.district,
            priority_score=p_res["total_score"],
            priority_level=p_res["priority_level"],
            status="open",
            distinct_reporter_count=1
        )
        db.add(new_inc)
        db.flush()

        petition.shared_incident_id = new_inc.id
        petition.status = "routed"
        task.resolution_action = "created_new"

    task.status = "resolved"
    task.resolved_by_user_id = current_user.id
    task.resolved_at = now_utc()

    audit = AuditEvent(
        user_id=current_user.id,
        user_role="officer",
        action="TRIAGE_TASK_RESOLVED",
        target_entity="triage_tasks",
        target_id=task.id,
        details={"action": payload.action}
    )
    db.add(audit)

    db.commit()
    return {"message": "Triage task resolved successfully"}
