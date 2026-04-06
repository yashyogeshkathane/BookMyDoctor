from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_patient
from app.schemas.patient_schema import (
    AppointmentResponse,
    BookAppointmentRequest,
    DoctorSlotsResponse,
    PatientBookedAppointmentItem,
    PaginatedDoctorListResponse,
)
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])
patient_service = PatientService()


@router.get("/doctors", response_model=PaginatedDoctorListResponse)
async def list_available_doctors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=8, ge=1, le=50),
    _: dict = Depends(get_current_patient),
) -> PaginatedDoctorListResponse:
    try:
        return await patient_service.list_available_doctors(page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load doctors right now. Please try again.",
        )


@router.get("/doctors/{doctor_id}/slots", response_model=DoctorSlotsResponse)
async def get_doctor_slots(
    doctor_id: str,
    date_value: date = Query(..., alias="date"),
    _: dict = Depends(get_current_patient),
) -> DoctorSlotsResponse:
    try:
        return await patient_service.get_doctor_slots(doctor_id=doctor_id, appointment_date=date_value)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load doctor slots right now. Please try again.",
        )


@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
async def book_appointment(
    payload: BookAppointmentRequest,
    patient_user: dict = Depends(get_current_patient),
) -> AppointmentResponse:
    try:
        return await patient_service.book_appointment(patient_user=patient_user, payload=payload)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to book appointment right now. Please try again.",
        )


@router.get("/appointments", response_model=list[PatientBookedAppointmentItem])
async def list_patient_appointments(
    patient_user: dict = Depends(get_current_patient),
) -> list[PatientBookedAppointmentItem]:
    try:
        return await patient_service.list_patient_appointments(patient_user=patient_user)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load your booked appointments right now. Please try again.",
        )
