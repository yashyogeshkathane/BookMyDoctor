from datetime import date

from fastapi import HTTPException, status

from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.user_repository import UserRepository
from app.schemas.doctor_schema import (
    DoctorOwnSlotItem,
    DoctorProfileResponse,
    DoctorSlotsOverviewResponse,
)


class DoctorService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.doctor_repository = DoctorRepository()
        self.appointment_repository = AppointmentRepository()

    async def get_my_profile(self, *, current_user: dict) -> DoctorProfileResponse:
        doctor = await self.doctor_repository.find_by_user_id(current_user["_id"])
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found.",
            )
        return DoctorProfileResponse(
            doctor_id=str(doctor["_id"]),
            user_id=str(doctor["user_id"]),
            name=current_user.get("name", ""),
            email=current_user.get("email", ""),
            phone=current_user.get("phone", ""),
            specialization=doctor.get("specialization", ""),
            experience_years=doctor.get("experience_years", 0),
            consultation_fees=float(doctor.get("consultation_fees", 0)),
            everyday_timing=doctor.get("everyday_timing") or {},
        )

    async def get_my_slots(self, *, current_user: dict, target_date: date) -> DoctorSlotsOverviewResponse:
        doctor = await self.doctor_repository.find_by_user_id(current_user["_id"])
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found.",
            )

        timing = doctor.get("everyday_timing") or {}
        start_time = timing.get("start_time")
        end_time = timing.get("end_time")
        if not start_time or not end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor timing is not configured.",
            )

        start_hour = int(start_time[:2])
        end_hour = int(end_time[:2])
        if end_hour <= start_hour:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor has invalid working window.",
            )

        date_key = target_date.isoformat()
        appointments = await self.appointment_repository.list_confirmed_slots(
            doctor_id=doctor["_id"],
            date_key=date_key,
        )
        patient_ids = [item.get("patient_id") for item in appointments if item.get("patient_id")]
        patients = await self.user_repository.list_by_ids(patient_ids)
        patients_by_id = {str(user["_id"]): user for user in patients}
        booked_by_start = {item.get("start_time"): item for item in appointments}

        slots: list[DoctorOwnSlotItem] = []
        for hour in range(start_hour, end_hour):
            slot_start = f"{hour:02d}:00"
            slot_end = f"{hour + 1:02d}:00"
            booked = booked_by_start.get(slot_start)
            if booked:
                patient = patients_by_id.get(str(booked.get("patient_id")), {})
                slots.append(
                    DoctorOwnSlotItem(
                        start_time=slot_start,
                        end_time=slot_end,
                        status="booked",
                        patient_name=patient.get("name"),
                        patient_email=patient.get("email"),
                    )
                )
            else:
                slots.append(
                    DoctorOwnSlotItem(
                        start_time=slot_start,
                        end_time=slot_end,
                        status="available",
                    )
                )

        return DoctorSlotsOverviewResponse(date=target_date, slots=slots)
