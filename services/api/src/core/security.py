import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from services.api.src.core.config import settings
from services.api.src.db.session import get_db
from services.api.src.db.models import User, Role, OTPSession

security_scheme = HTTPBearer()

def generate_mock_otp(phone_number: str) -> str:
    # Fixed predictable OTP for local development
    return "123456"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [r.name for r in current_user.roles]
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role required: {allowed_roles}. Current user roles: {user_roles}"
            )
        return current_user
    return role_checker

def redact_pii_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    # Mask Indian 10-digit phone numbers
    text = re.sub(r'\b[6-9]\d{9}\b', '[PHONE REDACTED]', text)
    # Mask emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]', text)
    return text

def redact_pii_for_shared_view(incident_dict: dict) -> dict:
    """Ensure shared incident responses do not leak citizen personal identifiers"""
    sanitized = incident_dict.copy()
    if 'citizen_name' in sanitized:
        sanitized['citizen_name'] = 'Anonymized Citizen'
    if 'phone_number' in sanitized:
        sanitized['phone_number'] = '[REDACTED]'
    if 'exact_address' in sanitized:
        sanitized['exact_address'] = '[STREET LEVEL ADDRESS REDACTED]'
    return sanitized
