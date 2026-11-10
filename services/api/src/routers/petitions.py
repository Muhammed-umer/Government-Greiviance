import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from services.api.src.db.session import get_db
from services.api.src.db.models import (
    Petition, PetitionAttachment, PetitionStatusHistory, SharedIncident, 
    GrievanceCategory, Department, User, Feedback, Appeal, TriageTask, 
    AuditEvent, now_utc
)
from services.api.src.schemas.schemas import PetitionCreate, PetitionOut, FeedbackCreate, AppealCreate
from services.api.src.core.security import get_current_user, require_roles
from services.api.src.services.ai.classifier import get_routing_adapter
from services.api.src.services.ai.duplicate import get_duplicate_adapter
from services.api.src.services.priority import calculate_priority_score
from services.api.src.core.config import settings

router = APIRouter(prefix="/petitions", tags=["Petitions"])

@router.post("", response_model=PetitionOut)
def create_petition(
    payload: PetitionCreate,
    current_user: User = Depends(require_roles(["citizen", "operator"])),
    db: Session = Depends(get_db)
):
    # Generate unique private Petition ID & number
    petition_num = f"PET-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"

    # 1. AI Department Classification & Routing
    router_adapter = get_routing_adapter(settings.AI_ROUTING_PROVIDER, settings.SARVAM_API_KEY)
    classification = router_adapter.classify(payload.title, payload.description)

    dept_code = classification["department_code"]
    category_code = classification["category_code"]
    confidence = classification["confidence"]

    dept = db.query(Department).filter(Department.code == dept_code).first()
    category = db.query(GrievanceCategory).filter(GrievanceCategory.code == category_code).first()

    if not dept:
        dept = db.query(Department).first()
    if not category:
        category = db.query(GrievanceCategory).first()

    # Create Petition record
    new_petition = Petition(
        petition_number=petition_num,
        citizen_id=current_user.id,
        language=payload.language,
        title=payload.title,
        description=payload.description,
        address=payload.address,
        landmark=payload.landmark,
        district=payload.district,
        pincode=payload.pincode,
        voice_transcript=payload.voice_transcript,
        status="submitted"
    )
    db.add(new_petition)
    db.flush()

    # Add initial status history
    history = PetitionStatusHistory(
        petition_id=new_petition.id,
        to_status="submitted",
        remarks=f"Petition submitted via portal. AI auto-route suggested department: {dept.name_en} (Confidence: {confidence}).",
        changed_by=current_user.id
    )
    db.add(history)

    # 2. Check for Low Confidence Routing (< 0.75 threshold) -> Human Triage Task
    if confidence < 0.75:
        triage_task = TriageTask(
            task_type="low_confidence_routing",
            petition_id=new_petition.id,
            confidence_score=confidence,
            suggested_department_id=dept.id if dept else None,
            status="pending"
        )
        db.add(triage_task)
        db.commit()
        db.refresh(new_petition)
        return new_petition

    # 3. AI Duplicate Detection & Linking
    dup_adapter = get_duplicate_adapter(settings.AI_DUPLICATE_PROVIDER)
    dup_result = dup_adapter.find_similar_incidents(
        db=db,
        category_id=category.id,
        district=payload.district,
        title=payload.title,
        description=payload.description,
        lat=payload.latitude,
        lng=payload.longitude
    )

    decision = dup_result["decision"]
    matched_id = dup_result["matched_incident_id"]

    if decision == "auto_link" and matched_id:
        incident = db.query(SharedIncident).filter(SharedIncident.id == matched_id).first()
        if incident:
            new_petition.shared_incident_id = incident.id
            new_petition.status = "linked"
            incident.distinct_reporter_count += 1
            
            # Recalculate priority
            p_res = calculate_priority_score(
                title=incident.title,
                summary=incident.summary,
                distinct_reporters_count=incident.distinct_reporter_count,
                landmark_location=payload.landmark
            )
            incident.priority_score = p_res["total_score"]
            incident.priority_level = p_res["priority_level"]

            link_history = PetitionStatusHistory(
                petition_id=new_petition.id,
                from_status="submitted",
                to_status="linked",
                remarks=f"Auto-linked to active shared incident {incident.incident_number} (Confidence: {dup_result['confidence']}).",
                changed_by=current_user.id
            )
            db.add(link_history)

    elif decision == "triage_task" and matched_id:
        triage_task = TriageTask(
            task_type="potential_duplicate_check",
            petition_id=new_petition.id,
            candidate_incident_id=matched_id,
            confidence_score=dup_result["confidence"],
            status="pending"
        )
        db.add(triage_task)

    else:
        # Create a NEW Shared Incident
        inc_num = f"INC-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate priority
        p_res = calculate_priority_score(
            title=payload.title,
            summary=payload.description,
            distinct_reporters_count=1,
            landmark_location=payload.landmark
        )

        sla_hours = category.default_sla_hours if category else 48
        sla_due = datetime.now(timezone.utc) + timedelta(hours=sla_hours)

        new_incident = SharedIncident(
            incident_number=inc_num,
            category_id=category.id,
            department_id=dept.id,
            title=payload.title,
            summary=payload.description,
            district=payload.district,
            priority_score=p_res["total_score"],
            priority_level=p_res["priority_level"],
            status="open",
            distinct_reporter_count=1,
            sla_hours=sla_hours,
            sla_due_at=sla_due,
            is_sensitive=category.is_sensitive if category else False
        )
        db.add(new_incident)
        db.flush()

        new_petition.shared_incident_id = new_incident.id
        new_petition.status = "routed"

    # Audit log
    audit = AuditEvent(
        user_id=current_user.id,
        user_role="citizen",
        action="PETITION_SUBMITTED",
        target_entity="petitions",
        target_id=new_petition.id,
        details={"petition_number": petition_num, "duplicate_decision": decision}
    )
    db.add(audit)

    db.commit()
    db.refresh(new_petition)
    return new_petition

@router.get("/me", response_model=List[PetitionOut])
def get_my_petitions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    petitions = db.query(Petition).filter(Petition.citizen_id == current_user.id).order_by(Petition.created_at.desc()).all()
    return petitions

@router.get("/{petition_id}", response_model=PetitionOut)
def get_petition_by_id(
    petition_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    petition = db.query(Petition).filter(Petition.id == petition_id).first()
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")
    
    # Restrict citizens to viewing only their own petitions
    user_roles = [r.name for r in current_user.roles]
    if "citizen" in user_roles and petition.citizen_id != current_user.id and "admin" not in user_roles:
        raise HTTPException(status_code=403, detail="Access denied. Citizens can only view their own petitions.")

    return petition

@router.post("/{petition_id}/attachments")
def upload_attachment(
    petition_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    petition = db.query(Petition).filter(Petition.id == petition_id).first()
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    if petition.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # File validation: MIME allowlist & 10MB size limit
    allowed_mimes = ["image/png", "image/jpeg", "application/pdf", "audio/mpeg", "audio/wav", "audio/ogg"]
    if file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not allowed.")

    file_bytes = file.file.read()
    if len(file_bytes) > 10 * 1024 * 1024: # 10MB
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    safe_filename = f"{petition_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
    storage_url = f"/static/uploads/{safe_filename}"

    attachment = PetitionAttachment(
        petition_id=petition_id,
        file_type=file.content_type,
        file_name=file.filename,
        file_size_bytes=len(file_bytes),
        storage_url=storage_url
    )
    db.add(attachment)
    db.commit()

    return {"message": "Attachment uploaded successfully", "storage_url": storage_url}

@router.post("/{petition_id}/feedback")
def submit_feedback(
    petition_id: str,
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    petition = db.query(Petition).filter(Petition.id == petition_id).first()
    if not petition or petition.citizen_id != current_user.id:
        raise HTTPException(status_code=404, detail="Petition not found")

    fb = Feedback(
        petition_id=petition_id,
        rating=payload.rating,
        comments=payload.comments
    )
    db.add(fb)
    db.commit()
    return {"message": "Thank you for your feedback!"}

@router.post("/{petition_id}/appeal")
def submit_appeal(
    petition_id: str,
    payload: AppealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    petition = db.query(Petition).filter(Petition.id == petition_id).first()
    if not petition or petition.citizen_id != current_user.id:
        raise HTTPException(status_code=404, detail="Petition not found")

    appeal = Appeal(
        petition_id=petition_id,
        reason=payload.reason,
        status="pending"
    )
    petition.status = "reopened"
    db.add(appeal)
    
    history = PetitionStatusHistory(
        petition_id=petition_id,
        from_status=petition.status,
        to_status="reopened",
        remarks=f"Appeal filed by citizen: {payload.reason}",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()

    return {"message": "Appeal submitted successfully. Your petition has been reopened for review."}
