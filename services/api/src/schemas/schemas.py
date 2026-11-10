from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field

# Auth Schemas
class OTPRequest(BaseModel):
    phone_number: str = Field(..., example="9876543210")
    role_requested: str = Field("citizen", example="citizen")

class OTPVerify(BaseModel):
    phone_number: str = Field(..., example="9876543210")
    otp_code: str = Field(..., example="123456")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Any

class RoleOut(BaseModel):
    id: str
    name: str

class UserOut(BaseModel):
    id: str
    phone_number: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    district: Optional[str] = None
    roles: List[RoleOut] = []

    class Config:
        from_attributes = True

# Petition Schemas
class PetitionCreate(BaseModel):
    title: str = Field(..., example="Street light not working in T. Nagar")
    description: str = Field(..., example="The street light near pillar 42 has been broken for 3 days.")
    language: str = Field("en", example="en") # ta, en, tanglish
    address: Optional[str] = None
    landmark: Optional[str] = None
    district: str = Field(..., example="Chennai")
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    voice_transcript: Optional[str] = None

class PetitionAttachmentOut(BaseModel):
    id: str
    file_type: str
    file_name: str
    storage_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class PetitionStatusHistoryOut(BaseModel):
    id: str
    from_status: Optional[str] = None
    to_status: str
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PetitionOut(BaseModel):
    id: str
    petition_number: str
    title: str
    description: str
    language: str
    address: Optional[str] = None
    landmark: Optional[str] = None
    district: str
    status: str
    shared_incident_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    attachments: List[PetitionAttachmentOut] = []
    history: List[PetitionStatusHistoryOut] = []

    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

class AppealCreate(BaseModel):
    reason: str = Field(..., min_length=10)

# Shared Incident Schemas
class IncidentOut(BaseModel):
    id: str
    incident_number: str
    title: str
    summary: str
    district: str
    category_name: Optional[str] = None
    department_name: Optional[str] = None
    priority_score: float
    priority_level: str
    status: str
    distinct_reporter_count: int
    linked_petitions_count: int = 0
    sla_hours: int
    sla_due_at: Optional[datetime] = None
    is_sla_breached: bool
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    summary: Optional[str] = None

class AssignCreate(BaseModel):
    assigned_to_user_id: str
    remarks: Optional[str] = None

class ActionCreate(BaseModel):
    action_type: str # status_update, field_visit, resolution
    notes: str
    evidence_url: Optional[str] = None

class PriorityOverrideCreate(BaseModel):
    new_priority: str # high, medium, low
    reason: str = Field(..., min_length=5) # MANDATORY

# Triage Schemas
class TriageTaskOut(BaseModel):
    id: str
    task_type: str
    petition_id: str
    petition_title: str
    candidate_incident_id: Optional[str] = None
    confidence_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TriageResolve(BaseModel):
    action: str # route, link, create_new
    target_department_id: Optional[str] = None
    target_incident_id: Optional[str] = None

# Admin Schemas
class DepartmentCreate(BaseModel):
    code: str
    name_en: str
    name_ta: str
    description: Optional[str] = None
    contact_email: Optional[str] = None

class CategoryCreate(BaseModel):
    department_id: str
    code: str
    name_en: str
    name_ta: str
    is_sensitive: bool = False
    default_sla_hours: int = 48

class SLAPolicyCreate(BaseModel):
    category_id: str
    priority_level: str
    resolution_hours: int
    escalation_hours: int

class AuditEventOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    action: str
    target_entity: str
    target_id: str
    details: Optional[Any] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class DashboardAnalytics(BaseModel):
    total_petitions: int
    total_incidents: int
    open_incidents: int
    high_priority_incidents: int
    sla_breached_incidents: int
    duplicate_link_rate: float
    avg_resolution_hours: float
    category_breakdown: List[dict]
