from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.user_model import UserRole, UserStatus


class DoctorProfileRegister(BaseModel):
    class EverydayTiming(BaseModel):
        start_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
        end_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")

        @model_validator(mode="after")
        def validate_time_window(self) -> "DoctorProfileRegister.EverydayTiming":
            start_minutes = int(self.start_time[:2]) * 60 + int(self.start_time[3:])
            end_minutes = int(self.end_time[:2]) * 60 + int(self.end_time[3:])
            if end_minutes <= start_minutes:
                raise ValueError("end_time must be later than start_time.")
            if end_minutes - start_minutes < 7 * 60:
                raise ValueError("Doctor everyday_timing must be at least 7 hours.")
            return self

    specialization: str = Field(..., min_length=2, max_length=120)
    experience_years: int = Field(default=0, ge=0, le=80)
    consultation_fees: float = Field(default=0, ge=0)
    everyday_timing: EverydayTiming


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole
    doctor_profile: Optional[DoctorProfileRegister] = None

    @model_validator(mode="after")
    def doctor_requires_profile(self) -> "UserRegisterRequest":
        if self.role == UserRole.DOCTOR and self.doctor_profile is None:
            raise ValueError("Doctor profile is required when registering as a doctor.")
        if self.role == UserRole.PATIENT and self.doctor_profile is not None:
            raise ValueError("Doctor profile must not be sent when registering as a patient.")
        return self


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=10)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AdminCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class AuthUserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str = ""
    role: UserRole
    user_status: UserStatus
    is_email_verified: bool
    created_at: datetime


class RegisterResponse(BaseModel):
    message: str
    user: AuthUserResponse
    verification_email_sent: bool
    verification_token: Optional[str] = None


class VerifyEmailResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class LogoutResponse(BaseModel):
    message: str
