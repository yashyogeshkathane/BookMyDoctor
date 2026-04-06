from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field

from app.models.base_model import TimestampMixin


class AppointmentStatus(str, Enum):
    AVAILABLE = "available"
    CONFIRMED = "confirmed"
    CANCELLED_BY_DOCTOR = "cancelled_by_doctor"
    CANCELLED_BY_PATIENT = "cancelled_by_patient"
    COMPLETED = "completed"


class Appointment(TimestampMixin):
    doctor_id: str
    patient_id: str
    date: datetime
    start_time: str
    end_time: str
    status: AppointmentStatus = AppointmentStatus.AVAILABLE
    reason: Optional[str] = None
