import inspect
from typing import Any, Optional

from app.config.database import get_database
from app.models.base_model import ObjectId


async def _run_db_call(callable_obj: Any, *args: Any, **kwargs: Any) -> Any:
    result = callable_obj(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


class DoctorRepository:
    @property
    def collection(self) -> Any:
        return get_database()["doctors"]

    async def create_doctor(self, doctor_document: dict[str, Any]) -> dict[str, Any]:
        insert_result = await _run_db_call(self.collection.insert_one, doctor_document)
        inserted_id = getattr(insert_result, "inserted_id", None)
        if inserted_id is not None:
            doctor_document["_id"] = inserted_id
        return doctor_document

    async def find_by_user_id(self, user_id: Any) -> Optional[dict[str, Any]]:
        normalized = user_id
        if isinstance(user_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(user_id):
            normalized = ObjectId(user_id)
        return await _run_db_call(self.collection.find_one, {"user_id": normalized})

    async def find_by_id(self, doctor_id: Any) -> Optional[dict[str, Any]]:
        normalized = doctor_id
        if isinstance(doctor_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(doctor_id):
            normalized = ObjectId(doctor_id)
        return await _run_db_call(self.collection.find_one, {"_id": normalized})

    async def update_by_user_id(self, user_id: Any, update_data: dict[str, Any]) -> None:
        normalized = user_id
        if isinstance(user_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(user_id):
            normalized = ObjectId(user_id)
        await _run_db_call(
            self.collection.update_one,
            {"user_id": normalized},
            {"$set": update_data},
        )

    async def list_doctors(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        records = await _run_db_call(cursor.to_list, length=None)
        return records or []

    async def count_doctors(self) -> int:
        return await _run_db_call(self.collection.count_documents, {})
