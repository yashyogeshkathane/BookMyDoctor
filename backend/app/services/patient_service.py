from datetime import date, datetime

from fastapi import HTTPException, status

from app.core.logger import get_logger
from app.models.user_model import UserRole, UserStatus
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.user_repository import UserRepository
from app.schemas.patient_schema import (
    AppointmentResponse,
    BookAppointmentRequest,
    DoctorListItem,
    DoctorSlotItem,
    DoctorSlotsResponse,
    PatientBookedAppointmentItem,
    PaginatedDoctorListResponse,
)

logger = get_logger("service.patient")


class PatientService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.doctor_repository = DoctorRepository()
        self.appointment_repository = AppointmentRepository()

    async def list_patient_appointments(self, *, patient_user: dict) -> list[PatientBookedAppointmentItem]:
        if patient_user.get("role") != UserRole.PATIENT.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can view booked appointments.",
            )

        appointments = await self.appointment_repository.list_by_patient(patient_id=patient_user["_id"])
        doctor_ids = list({item.get("doctor_id") for item in appointments if item.get("doctor_id") is not None})
        doctors = await self.doctor_repository.collection.find({"_id": {"$in": doctor_ids}}).to_list(length=None)
        doctors_by_id = {str(doc["_id"]): doc for doc in (doctors or [])}
        doctor_user_ids = [doc.get("user_id") for doc in doctors_by_id.values() if doc.get("user_id")]
        doctor_users = await self.user_repository.list_by_ids(doctor_user_ids)
        users_by_id = {str(user["_id"]): user for user in doctor_users}

        items: list[PatientBookedAppointmentItem] = []
        for appt in appointments:
            doctor = doctors_by_id.get(str(appt.get("doctor_id")))
            doctor_user = users_by_id.get(str((doctor or {}).get("user_id")))
            appt_date = appt.get("date")
            if isinstance(appt_date, datetime):
                appt_date = appt_date.date()
            elif isinstance(appt_date, str):
                appt_date = date.fromisoformat(appt_date[:10])
            items.append(
                PatientBookedAppointmentItem(
                    id=str(appt["_id"]),
                    doctor_id=str(appt["doctor_id"]),
                    doctor_name=(doctor_user or {}).get("name", "Doctor"),
                    specialization=(doctor or {}).get("specialization", ""),
                    date=appt_date,
                    start_time=appt.get("start_time", ""),
                    end_time=appt.get("end_time", ""),
                    status=appt.get("status", ""),
                    reason=appt.get("reason"),
                    created_at=appt.get("created_at", datetime.utcnow()),
                )
            )
        return items

    async def list_available_doctors(self, *, page: int, page_size: int) -> PaginatedDoctorListResponse:
        total = await self.doctor_repository.count_doctors()
        doctor_records = await self.doctor_repository.list_doctors(
            skip=(page - 1) * page_size,
            limit=page_size,
        )
        user_ids = [record.get("user_id") for record in doctor_records if record.get("user_id")]
        users = await self.user_repository.list_by_ids(user_ids)
        users_by_id = {str(user["_id"]): user for user in users}

        items: list[DoctorListItem] = []
        for record in doctor_records:
            user = users_by_id.get(str(record.get("user_id")))
            if not user:
                continue
            if user.get("role") != UserRole.DOCTOR.value:
                continue
            if user.get("user_status") != UserStatus.ACTIVE.value:
                continue
            items.append(
                DoctorListItem(
                    doctor_id=str(record["_id"]),
                    user_id=str(record["user_id"]),
                    name=user.get("name") or "",
                    email=user.get("email") or "",
                    phone=user.get("phone") or "",
                    specialization=record.get("specialization") or "",
                    experience_years=record.get("experience_years") or 0,
                    consultation_fees=float(record.get("consultation_fees") or 0),
                    everyday_timing=record.get("everyday_timing") or {},
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return PaginatedDoctorListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )

    async def get_doctor_slots(self, *, doctor_id: str, appointment_date: date) -> DoctorSlotsResponse:
        doctor = await self.doctor_repository.find_by_id(doctor_id)
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

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

        date_key = appointment_date.isoformat()
        confirmed = await self.appointment_repository.list_confirmed_slots(
            doctor_id=doctor["_id"],
            date_key=date_key,
        )
        booked_starts = {item.get("start_time") for item in confirmed}

        slots: list[DoctorSlotItem] = []
        for hour in range(start_hour, end_hour):
            slot_start = f"{hour:02d}:00"
            slot_end = f"{hour + 1:02d}:00"
            if slot_start in booked_starts:
                continue
            slots.append(DoctorSlotItem(start_time=slot_start, end_time=slot_end, status="available"))

        doctor_user = await self.user_repository.find_by_id(doctor["user_id"])
        return DoctorSlotsResponse(
            doctor_id=str(doctor["_id"]),
            doctor_name=(doctor_user or {}).get("name", "Doctor"),
            date=appointment_date,
            slots=slots,
        )

    async def book_appointment(
        self,
        *,
        patient_user: dict,
        payload: BookAppointmentRequest,
    ) -> AppointmentResponse:
        if patient_user.get("role") != UserRole.PATIENT.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can book appointments.",
            )

        doctor = await self.doctor_repository.find_by_id(payload.doctor_id)
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

        timing = doctor.get("everyday_timing") or {}
        working_start = timing.get("start_time")
        working_end = timing.get("end_time")
        if not working_start or not working_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor timing is not configured.",
            )

        start_hour = int(payload.start_time[:2])
        end_time = f"{start_hour + 1:02d}:00"
        if payload.start_time[-2:] != "00":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only hourly slots are allowed (HH:00).",
            )
        if payload.start_time < working_start or end_time > working_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected slot is outside doctor working hours.",
            )
        date_key = payload.date.isoformat()

        already_booked = await self.appointment_repository.slot_exists(
            doctor_id=doctor["_id"],
            date_key=date_key,
            start_time=payload.start_time,
        )
        if already_booked:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This slot has already been booked.",
            )

        now = datetime.utcnow()
        appointment_document = {
            "doctor_id": doctor["_id"],
            "patient_id": patient_user["_id"],
            "date": datetime.combine(payload.date, datetime.min.time()),
            "date_key": date_key,
            "start_time": payload.start_time,
            "end_time": end_time,
            "status": "confirmed",
            "reason": payload.reason,
            "created_at": now,
            "updated_at": now,
        }
        try:
            created = await self.appointment_repository.create_appointment(appointment_document)
        except self.appointment_repository.SlotAlreadyBookedError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This slot has already been booked.",
            ) from exc
        logger.info(
            "Appointment booked: appointment_id=%s doctor_id=%s patient_id=%s date=%s start=%s",
            str(created["_id"]),
            str(created["doctor_id"]),
            str(created["patient_id"]),
            date_key,
            created["start_time"],
        )
        return AppointmentResponse(
            id=str(created["_id"]),
            doctor_id=str(created["doctor_id"]),
            patient_id=str(created["patient_id"]),
            date=payload.date,
            start_time=created["start_time"],
            end_time=created["end_time"],
            status=created["status"],
            reason=created.get("reason"),
            created_at=created["created_at"],
        )
