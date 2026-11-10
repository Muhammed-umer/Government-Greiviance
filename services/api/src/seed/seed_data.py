import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from services.api.src.db.session import SessionLocal, engine
from services.api.src.db.models import (
    Base, User, Role, Department, Office, Service, GrievanceCategory, 
    Petition, SharedIncident, PetitionStatusHistory, SLAPolicy, AuditEvent, now_utc
)
from services.api.src.services.priority import calculate_priority_score

def seed_database():
    print("🌱 Initializing Tamil Nadu Grievance Portal Database Seeding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Roles
        roles_dict = {}
        role_names = ["citizen", "operator", "officer", "supervisor", "admin", "auditor"]
        for r_name in role_names:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=f"{r_name.capitalize()} role")
                db.add(role)
                db.flush()
            roles_dict[r_name] = role

        # 2. Seed Users
        def get_or_create_user(phone, name, email, district, role_name):
            u = db.query(User).filter(User.phone_number == phone).first()
            if not u:
                u = User(
                    phone_number=phone,
                    full_name=name,
                    email=email,
                    district=district
                )
                u.roles.append(roles_dict[role_name])
                db.add(u)
                db.flush()
            return u

        citizen1 = get_or_create_user("9876543210", "Kavitha Sundaram", "kavitha@example.tn.gov.in", "Chennai", "citizen")
        citizen2 = get_or_create_user("9876543211", "Muralidharan V", "murali@example.tn.gov.in", "Chennai", "citizen")
        officer1 = get_or_create_user("9000000001", "Officer Selvam R (AE TANGEDCO)", "selvam@tangedco.gov.in", "Chennai", "officer")
        supervisor1 = get_or_create_user("9000000002", "Superintendent Anbarasan", "superintendent@gcc.gov.in", "Chennai", "supervisor")
        admin1 = get_or_create_user("9999999999", "System Admin (TN e-Governance)", "admin@tnega.tn.gov.in", "Chennai", "admin")

        # 3. Seed Departments
        dept_data = [
            ("GCC", "Greater Chennai Corporation", "பெருநகர சென்னை மாநகராட்சி"),
            ("TANGEDCO", "Tamil Nadu Electricity Board (TANGEDCO)", "தமிழ்நாடு மின்சார வாரியம்"),
            ("CMWSSB", "Chennai Metro Water (CMWSSB)", "சென்னை குடிநீர் வாரியம்"),
            ("TRAFFIC", "Traffic Police & Road Safety", "போக்குவரத்து காவல்துறை"),
            ("REVENUE", "Revenue & Disaster Management", "வருவாய் துறை"),
            ("HEALTH", "Public Health Department", "பொது சுகாதாரத் துறை")
        ]

        depts_map = {}
        for code, en, ta in dept_data:
            d = db.query(Department).filter(Department.code == code).first()
            if not d:
                d = Department(code=code, name_en=en, name_ta=ta, contact_email=f"info@{code.lower()}.tn.gov.in")
                db.add(d)
                db.flush()
            depts_map[code] = d

        # 4. Seed Categories
        cat_data = [
            ("TANGEDCO", "ELEC_OUTAGE", "Power Outage / Transformer Fault", "மின்சார விநியோகம் / டிரான்ஸ்பார்மர் கோளாறு", False, 24),
            ("TANGEDCO", "ELEC_WIRE_HAZARD", "Live Wire / Danger Pole", "அபாயகரமான மின் கம்பி", True, 4), # Life safety immediate
            ("CMWSSB", "WATER_LEAK", "Drinking Water Supply Pipeline Leakage", "குடிநீர் குழாய் கசிவு", False, 48),
            ("GCC", "GARBAGE_CLEAN", "Garbage Bin Overflow / Sanitation", "குப்பை தொட்டி நிரம்பி வழிதல்", False, 24),
            ("GCC", "MANHOLE_OPEN", "Open Storm Drain / Manhole Danger", "திறந்தவெளி சாக்கடை மூடி அபாயம்", True, 6), # Life safety
            ("TRAFFIC", "TRAFFIC_SIGNAL", "Traffic Light Malfunction", "போக்குவரத்து சிக்னல் வேலை செய்யவில்லை", False, 12),
            ("REVENUE", "CORRUPTION_ALLEGATION", "Administrative Corruption / Entitlement Dispute", "நிர்வாக லஞ்ச புகார்கள்", True, 72)
        ]

        cat_map = {}
        for d_code, c_code, en, ta, is_sens, sla_h in cat_data:
            c = db.query(GrievanceCategory).filter(GrievanceCategory.code == c_code).first()
            if not c:
                c = GrievanceCategory(
                    department_id=depts_map[d_code].id,
                    code=c_code,
                    name_en=en,
                    name_ta=ta,
                    is_sensitive=is_sens,
                    default_sla_hours=sla_h
                )
                db.add(c)
                db.flush()
            cat_map[c_code] = c

        # 5. Seed Demo Petitions & Shared Incidents
        demo_tickets = [
            {
                "title": "Street light pole broken near T. Nagar Bus Stand",
                "desc": "எங்கள் தெருவில் 3 நாட்களாக மின்சார விளக்கு எரியவில்லை, T. Nagar பஸ் ஸ்டாண்ட் அருகில் தரைக்கடியில் தீப்பொறி வருகிறது.",
                "lang": "ta",
                "cat": "ELEC_WIRE_HAZARD",
                "dept": "TANGEDCO",
                "district": "Chennai",
                "landmark": "T. Nagar Bus Stand",
                "citizen": citizen1
            },
            {
                "title": "Current pochu in Anna Nagar 4th Block",
                "desc": "Anna Nagar 4th block full power cutout since morning 6 AM. Please repair immediately.",
                "lang": "tanglish",
                "cat": "ELEC_OUTAGE",
                "dept": "TANGEDCO",
                "district": "Chennai",
                "landmark": "Anna Nagar 4th Block Tower Park",
                "citizen": citizen2
            },
            {
                "title": "Garbage dumping and bad smell in Velachery Road",
                "desc": "Huge pile of solid waste dumped near Velachery main road. Rain water stagnant inside bin.",
                "lang": "en",
                "cat": "GARBAGE_CLEAN",
                "dept": "GCC",
                "district": "Chennai",
                "landmark": "Velachery Railway Station",
                "citizen": citizen1
            }
        ]

        for idx, t in enumerate(demo_tickets, 1):
            pet_num = f"PET-2026-DEMO00{idx}"
            p = db.query(Petition).filter(Petition.petition_number == pet_num).first()
            if not p:
                p = Petition(
                    petition_number=pet_num,
                    citizen_id=t["citizen"].id,
                    language=t["lang"],
                    title=t["title"],
                    description=t["desc"],
                    district=t["district"],
                    landmark=t["landmark"],
                    status="routed"
                )
                db.add(p)
                db.flush()

                # Calculate Priority
                cat_obj = cat_map[t["cat"]]
                dept_obj = depts_map[t["dept"]]
                p_res = calculate_priority_score(
                    title=t["title"],
                    summary=t["desc"],
                    distinct_reporters_count=1,
                    landmark_location=t["landmark"]
                )

                inc_num = f"INC-2026-DEMO00{idx}"
                sla_due = datetime.now(timezone.utc) + timedelta(hours=cat_obj.default_sla_hours)

                inc = SharedIncident(
                    incident_number=inc_num,
                    category_id=cat_obj.id,
                    department_id=dept_obj.id,
                    title=t["title"],
                    summary=t["desc"],
                    district=t["district"],
                    priority_score=p_res["total_score"],
                    priority_level=p_res["priority_level"],
                    status="open",
                    distinct_reporter_count=1,
                    sla_hours=cat_obj.default_sla_hours,
                    sla_due_at=sla_due,
                    is_sensitive=cat_obj.is_sensitive
                )
                db.add(inc)
                db.flush()

                p.shared_incident_id = inc.id
                p.status = "linked"

                history = PetitionStatusHistory(
                    petition_id=p.id,
                    to_status="linked",
                    remarks="Linked to initial demo shared incident.",
                    changed_by=admin1.id
                )
                db.add(history)

        db.commit()
        print("✅ Seeding completed successfully! Demo data loaded.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
