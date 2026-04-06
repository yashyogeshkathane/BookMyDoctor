from datetime import date
from typing import Optional

from pydantic import BaseModel


class DoctorProfileResponse(BaseModel):
    doctor_id: str
    user_id: str
    name: str
    email: str
    phone: str
    specialization: str
    experience_years: int
    consultation_fees: float
    everyday_timing: dict[str, str]


class DoctorOwnSlotItem(BaseModel):
    start_time: str
    end_time: str
    status: str
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None


class DoctorSlotsOverviewResponse(BaseModel):
    date: date
    slots: list[DoctorOwnSlotItem]
