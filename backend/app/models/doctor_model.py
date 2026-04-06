from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.base_model import TimestampMixin


class DoctorEverydayTiming(BaseModel):
    start_time: str
    end_time: str


class Doctor(TimestampMixin):
    """MongoDB `doctors` document shape."""

    user_id: str
    specialization: str
    experience_years: int = 0
    consultation_fees: float = 0
    everyday_timing: DoctorEverydayTiming
    approved_at: Optional[datetime] = None
