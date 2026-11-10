import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Table, Index
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from services.api.src.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def now_utc():
    return datetime.now(timezone.utc)

# User Roles Link Table
user_roles_table = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', String(36), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)  # citizen, operator, officer, supervisor, admin, auditor
    description = Column(String(255), nullable=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    roles = relationship('Role', secondary=user_roles_table, backref='users')
    petitions = relationship('Petition', back_populates='citizen')

class OTPSession(Base):
    __tablename__ = 'otp_sessions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone_number = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    role_requested = Column(String(50), default='citizen')
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False) # GCC, TANGEDCO, CMWSSB, TRAFFIC, REVENUE, HEALTH
    name_en = Column(String(150), nullable=False)
    name_ta = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    offices = relationship('Office', back_populates='department')
    services = relationship('Service', back_populates='department')
    categories = relationship('GrievanceCategory', back_populates='department')

class Office(Base):
    __tablename__ = 'offices'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    name = Column(String(150), nullable=False)
    district = Column(String(100), nullable=False)
    taluk_zone = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    location = Column(Geometry('POINT', srid=4326), nullable=True)

    department = relationship('Department', back_populates='offices')

class Service(Base):
    __tablename__ = 'services'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    name_en = Column(String(150), nullable=False)
    name_ta = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False)

    department = relationship('Department', back_populates='services')

class GrievanceCategory(Base):
    __tablename__ = 'grievance_categories'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    name_en = Column(String(150), nullable=False)
    name_ta = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False) # Sensitive: corruption, abuse, domestic violence - NO AUTO LINK
    default_sla_hours = Column(Integer, default=48)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    department = relationship('Department', back_populates='categories')

class RoutingRule(Base):
    __tablename__ = 'routing_rules'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey('grievance_categories.id'), nullable=False)
    district = Column(String(100), nullable=True)
    target_department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    target_office_id = Column(String(36), ForeignKey('offices.id'), nullable=True)
    keywords = Column(JSON, nullable=True) # list of terms in English/Tamil/Tanglish

class Petition(Base):
    __tablename__ = 'petitions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    petition_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. PET-2026-0001
    citizen_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    shared_incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=True)
    
    language = Column(String(10), default='en') # ta, en, tanglish
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    voice_recording_url = Column(String(500), nullable=True)
    voice_transcript = Column(Text, nullable=True)
    
    address = Column(Text, nullable=True)
    landmark = Column(String(255), nullable=True)
    district = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=True)
    location = Column(Geometry('POINT', srid=4326), nullable=True)

    status = Column(String(50), default='submitted', index=True) # submitted, routed, linked, under_review, in_progress, resolved, rejected, reopened
    created_at = Column(DateTime(timezone=True), default=now_utc, index=True)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    citizen = relationship('User', back_populates='petitions')
    shared_incident = relationship('SharedIncident', back_populates='petitions')
    attachments = relationship('PetitionAttachment', back_populates='petition', cascade='all, delete-orphan')
    history = relationship('PetitionStatusHistory', back_populates='petition', cascade='all, delete-orphan')
    feedbacks = relationship('Feedback', back_populates='petition')
    appeals = relationship('Appeal', back_populates='petition')

class PetitionAttachment(Base):
    __tablename__ = 'petition_attachments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    petition_id = Column(String(36), ForeignKey('petitions.id'), nullable=False)
    file_type = Column(String(50), nullable=False) # image/png, application/pdf, audio/wav
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    storage_url = Column(String(500), nullable=False)
    checksum = Column(String(64), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=now_utc)

    petition = relationship('Petition', back_populates='attachments')

class PetitionStatusHistory(Base):
    __tablename__ = 'petition_status_history'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    petition_id = Column(String(36), ForeignKey('petitions.id'), nullable=False)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    changed_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    petition = relationship('Petition', back_populates='history')

class SharedIncident(Base):
    __tablename__ = 'shared_incidents'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. INC-2026-0001
    category_id = Column(String(36), ForeignKey('grievance_categories.id'), nullable=False)
    department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    office_id = Column(String(36), ForeignKey('offices.id'), nullable=True)
    
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    district = Column(String(100), nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=True)
    embedding = Column(Vector(1536), nullable=True) # Vector embedding for pgvector duplicate search

    priority_score = Column(Float, default=20.0) # 0-100 score
    priority_level = Column(String(20), default='low', index=True) # high, medium, low
    status = Column(String(50), default='open', index=True) # open, assigned, field_verified, in_progress, resolved, closed

    distinct_reporter_count = Column(Integer, default=1)
    is_sensitive = Column(Boolean, default=False)

    sla_hours = Column(Integer, default=48)
    sla_due_at = Column(DateTime(timezone=True), nullable=True)
    is_sla_breached = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=now_utc, index=True)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    petitions = relationship('Petition', back_populates='shared_incident')
    category = relationship('GrievanceCategory')
    department = relationship('Department')
    office = relationship('Office')
    assignments = relationship('Assignment', back_populates='incident')
    actions = relationship('OfficerAction', back_populates='incident')
    verifications = relationship('FieldVerification', back_populates='incident')
    priority_overrides = relationship('PriorityOverride', back_populates='incident')

class IncidentPetitionLink(Base):
    __tablename__ = 'incident_petition_links'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=False)
    petition_id = Column(String(36), ForeignKey('petitions.id'), nullable=False)
    confidence_score = Column(Float, nullable=False)
    link_reason = Column(String(255), nullable=True) # auto_linked, officer_linked
    linked_at = Column(DateTime(timezone=True), default=now_utc)

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=False)
    assigned_to_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    assigned_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default='assigned')
    remarks = Column(Text, nullable=True)
    assigned_at = Column(DateTime(timezone=True), default=now_utc)

    incident = relationship('SharedIncident', back_populates='assignments')

class OfficerAction(Base):
    __tablename__ = 'officer_actions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=False)
    officer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50), nullable=False) # status_update, field_visit, resolution, escalation
    notes = Column(Text, nullable=False)
    evidence_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    incident = relationship('SharedIncident', back_populates='actions')

class FieldVerification(Base):
    __tablename__ = 'field_verifications'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=False)
    officer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    verification_status = Column(String(50), nullable=False) # verified_true, invalid_complaint, partially_resolved
    remarks = Column(Text, nullable=False)
    photo_evidence_url = Column(String(500), nullable=True)
    location = Column(Geometry('POINT', srid=4326), nullable=True)
    verified_at = Column(DateTime(timezone=True), default=now_utc)

    incident = relationship('SharedIncident', back_populates='verifications')

class SLAPolicy(Base):
    __tablename__ = 'sla_policies'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey('grievance_categories.id'), nullable=False)
    priority_level = Column(String(20), nullable=False) # high, medium, low
    resolution_hours = Column(Integer, nullable=False)
    escalation_hours = Column(Integer, nullable=False)

class PriorityAssessment(Base):
    __tablename__ = 'priority_assessments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=False)
    safety_severity = Column(Float, default=0.0) # 0-40
    verified_public_impact = Column(Float, default=0.0) # 0-25
    critical_location = Column(Float, default=0.0) # 0-15
    sla_risk = Column(Float, default=0.0) # 0-10
    recurrence = Column(Float, default=0.0) # 0-10
    total_score = Column(Float, default=0.0)
    calculated_at = Column(DateTime(timezone=True), default=now_utc)

class PriorityOverride(Base):
    __tablename__ = 'priority_overrides'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=False)
    officer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    previous_priority = Column(String(20), nullable=False)
    new_priority = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False) # MANDATORY EXPLANATION
    created_at = Column(DateTime(timezone=True), default=now_utc)

    incident = relationship('SharedIncident', back_populates='priority_overrides')

class AIInference(Base):
    __tablename__ = 'ai_inferences'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    inference_type = Column(String(50), nullable=False) # stt, tts, routing, duplicate_check
    provider = Column(String(50), nullable=False) # mock, sarvam, indicbert, qwen
    model_version = Column(String(50), nullable=False)
    input_metadata = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    final_decision = Column(String(100), nullable=True)
    is_overridden = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class TriageTask(Base):
    __tablename__ = 'triage_tasks'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_type = Column(String(50), nullable=False) # low_confidence_routing, potential_duplicate_check
    petition_id = Column(String(36), ForeignKey('petitions.id'), nullable=False)
    candidate_incident_id = Column(String(36), ForeignKey('shared_incidents.id'), nullable=True)
    confidence_score = Column(Float, nullable=False)
    suggested_department_id = Column(String(36), ForeignKey('departments.id'), nullable=True)
    status = Column(String(50), default='pending') # pending, resolved, rejected
    resolution_action = Column(String(50), nullable=True) # routed, linked, created_new
    resolved_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    petition_id = Column(String(36), ForeignKey('petitions.id'), nullable=False)
    rating = Column(Integer, nullable=False) # 1-5 stars
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    petition = relationship('Petition', back_populates='feedbacks')

class Appeal(Base):
    __tablename__ = 'appeals'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    petition_id = Column(String(36), ForeignKey('petitions.id'), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default='pending') # pending, approved, rejected
    reviewed_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    petition = relationship('Petition', back_populates='appeals')

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    user_role = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False) # e.g. PETITION_SUBMITTED, PRIORITY_OVERRIDDEN, INCIDENT_RESOLVED
    target_entity = Column(String(100), nullable=False)
    target_id = Column(String(36), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=now_utc, index=True)
