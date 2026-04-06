from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_doctor
from app.schemas.doctor_schema import DoctorProfileResponse, DoctorSlotsOverviewResponse
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["Doctors"])
doctor_service = DoctorService()


@router.get("/me", response_model=DoctorProfileResponse)
async def get_my_profile(
    current_doctor: dict = Depends(get_current_doctor),
) -> DoctorProfileResponse:
    try:
        return await doctor_service.get_my_profile(current_user=current_doctor)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load doctor profile right now. Please try again.",
        )


@router.get("/slots", response_model=DoctorSlotsOverviewResponse)
async def get_my_slots(
    date_value: date = Query(..., alias="date"),
    current_doctor: dict = Depends(get_current_doctor),
) -> DoctorSlotsOverviewResponse:
    try:
        return await doctor_service.get_my_slots(current_user=current_doctor, target_date=date_value)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load doctor slots right now. Please try again.",
        )
