from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.base_model import TimestampMixin


class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class UserStatus(str, Enum):
    PENDING_EMAIL_VERIFICATION = "pending_email_verification"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"


class EmailVerificationToken(BaseModel):
    token_hash: str
    expires_at: datetime
    sent_at: datetime
    verified_at: Optional[datetime] = None


class RefreshTokenSession(BaseModel):
    token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class User(TimestampMixin):
    name: str
    email: EmailStr
    phone: str = ""
    password_hash: str
    role: UserRole = UserRole.PATIENT
    user_status: UserStatus = UserStatus.PENDING_EMAIL_VERIFICATION
    is_email_verified: bool = False
    is_active: bool = True
    email_verification: Optional[EmailVerificationToken] = None
    refresh_tokens: list[RefreshTokenSession] = Field(default_factory=list)
