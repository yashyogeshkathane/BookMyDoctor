from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class DoctorListItem(BaseModel):
    doctor_id: str
    user_id: str
    name: str
    email: str
    phone: str
    specialization: str
    experience_years: int
    consultation_fees: float
    everyday_timing: dict[str, str]


class PaginatedDoctorListResponse(BaseModel):
    items: list[DoctorListItem]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class DoctorSlotItem(BaseModel):
    start_time: str
    end_time: str
    status: str


class DoctorSlotsResponse(BaseModel):
    doctor_id: str
    doctor_name: str
    date: date
    slots: list[DoctorSlotItem]


class BookAppointmentRequest(BaseModel):
    doctor_id: str = Field(..., min_length=24, max_length=24)
    date: date
    start_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    reason: Optional[str] = Field(default=None, max_length=500)


class AppointmentResponse(BaseModel):
    id: str
    doctor_id: str
    patient_id: str
    date: date
    start_time: str
    end_time: str
    status: str
    reason: Optional[str] = None
    created_at: datetime


class PatientBookedAppointmentItem(BaseModel):
    id: str
    doctor_id: str
    doctor_name: str
    specialization: str
    date: date
    start_time: str
    end_time: str
    status: str
    reason: Optional[str] = None
    created_at: datetime
