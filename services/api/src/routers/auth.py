from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.api.src.db.session import get_db
from services.api.src.db.models import User, Role, OTPSession
from services.api.src.schemas.schemas import OTPRequest, OTPVerify, TokenResponse, UserOut
from services.api.src.core.security import generate_mock_otp, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/request-otp")
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    otp_code = generate_mock_otp(payload.phone_number)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    session = OTPSession(
        phone_number=payload.phone_number,
        otp_code=otp_code,
        role_requested=payload.role_requested,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()

    return {
        "message": f"OTP sent successfully to {payload.phone_number}",
        "dev_mock_otp": otp_code, # Convenience hint for local testing
        "expires_in_minutes": 10
    }

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)):
    # Local dev verification: accepts '123456' or valid OTP session
    if payload.otp_code != "123456":
        session = db.query(OTPSession).filter(
            OTPSession.phone_number == payload.phone_number,
            OTPSession.otp_code == payload.otp_code,
            OTPSession.is_used == False
        ).order_by(OTPSession.created_at.desc()).first()

        if not session:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP code")
        session.is_used = True

    # Find or create user
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        user = User(
            phone_number=payload.phone_number,
            full_name=f"User {payload.phone_number[-4:]}",
            district="Chennai"
        )
        db.add(user)
        db.flush()

        # Assign default citizen role
        citizen_role = db.query(Role).filter(Role.name == "citizen").first()
        if not citizen_role:
            citizen_role = Role(name="citizen", description="Citizen role")
            db.add(citizen_role)
            db.flush()
        user.roles.append(citizen_role)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": user.id, "phone": user.phone_number})
    
    # Return formatted UserOut data
    roles_out = [{"id": r.id, "name": r.name} for r in user.roles]
    user_data = {
        "id": user.id,
        "phone_number": user.phone_number,
        "full_name": user.full_name,
        "email": user.email,
        "district": user.district,
        "roles": roles_out
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
