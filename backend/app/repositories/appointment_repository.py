import inspect
from typing import Any

from app.config.database import get_database
from app.models.base_model import ObjectId
from pymongo.errors import DuplicateKeyError


async def _run_db_call(callable_obj: Any, *args: Any, **kwargs: Any) -> Any:
    result = callable_obj(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


class AppointmentRepository:
    """Data access for the `appointments` collection."""

    @property
    def collection(self) -> Any:
        return get_database()["appointments"]

    class SlotAlreadyBookedError(Exception):
        pass

    async def create_appointment(self, appointment_document: dict[str, Any]) -> dict[str, Any]:
        try:
            insert_result = await _run_db_call(self.collection.insert_one, appointment_document)
        except DuplicateKeyError as exc:
            raise self.SlotAlreadyBookedError("This slot has already been booked.") from exc
        inserted_id = getattr(insert_result, "inserted_id", None)
        if inserted_id is not None:
            appointment_document["_id"] = inserted_id
        return appointment_document

    async def list_confirmed_slots(
        self,
        *,
        doctor_id: Any,
        date_key: str,
    ) -> list[dict[str, Any]]:
        normalized_doctor_id = doctor_id
        if isinstance(doctor_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(doctor_id):
            normalized_doctor_id = ObjectId(doctor_id)
        cursor = self.collection.find(
            {
                "doctor_id": normalized_doctor_id,
                "date_key": date_key,
                "status": "confirmed",
            }
        )
        records = await _run_db_call(cursor.to_list, length=None)
        return records or []

    async def slot_exists(
        self,
        *,
        doctor_id: Any,
        date_key: str,
        start_time: str,
    ) -> bool:
        normalized_doctor_id = doctor_id
        if isinstance(doctor_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(doctor_id):
            normalized_doctor_id = ObjectId(doctor_id)
        count = await _run_db_call(
            self.collection.count_documents,
            {
                "doctor_id": normalized_doctor_id,
                "date_key": date_key,
                "start_time": start_time,
                "status": "confirmed",
            },
        )
        return count > 0

    async def list_by_patient(self, *, patient_id: Any) -> list[dict[str, Any]]:
        normalized_patient_id = patient_id
        if isinstance(patient_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(patient_id):
            normalized_patient_id = ObjectId(patient_id)
        cursor = self.collection.find({"patient_id": normalized_patient_id}).sort("created_at", -1)
        records = await _run_db_call(cursor.to_list, length=None)
        return records or []
