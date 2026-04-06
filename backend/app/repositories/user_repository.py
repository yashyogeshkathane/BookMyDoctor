import inspect
from typing import Any, Optional

from app.config.database import get_database
from app.models.base_model import ObjectId


async def _run_db_call(callable_obj: Any, *args: Any, **kwargs: Any) -> Any:
    result = callable_obj(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


class UserRepository:
    @property
    def collection(self) -> Any:
        return get_database()["users"]

    async def find_by_email(self, email: str) -> Optional[dict[str, Any]]:
        return await _run_db_call(self.collection.find_one, {"email": email})

    async def email_exists(self, email: str) -> bool:
        return await self.find_by_email(email) is not None

    async def find_by_id(self, user_id: Any) -> Optional[dict[str, Any]]:
        normalized_user_id = user_id
        if isinstance(user_id, str) and hasattr(ObjectId, "is_valid") and ObjectId.is_valid(user_id):
            normalized_user_id = ObjectId(user_id)
        return await _run_db_call(self.collection.find_one, {"_id": normalized_user_id})

    async def find_by_verification_token_hash(self, token_hash: str) -> Optional[dict[str, Any]]:
        return await _run_db_call(
            self.collection.find_one,
            {"email_verification.token_hash": token_hash},
        )

    async def list_by_role(
        self,
        role: str,
        *,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        users_cursor = self.collection.find({"role": role}).sort("created_at", -1).skip(skip)
        if limit is not None:
            users_cursor = users_cursor.limit(limit)
        users = await _run_db_call(users_cursor.to_list, length=None)
        return users or []

    async def count_by_role(self, role: str) -> int:
        return await _run_db_call(self.collection.count_documents, {"role": role})

    async def list_by_filters(
        self,
        filters: dict[str, Any],
        *,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        users_cursor = self.collection.find(filters).sort("created_at", -1).skip(skip)
        if limit is not None:
            users_cursor = users_cursor.limit(limit)
        users = await _run_db_call(users_cursor.to_list, length=None)
        return users or []

    async def count_by_filters(self, filters: dict[str, Any]) -> int:
        return await _run_db_call(self.collection.count_documents, filters)

    async def list_by_ids(self, user_ids: list[Any]) -> list[dict[str, Any]]:
        if not user_ids:
            return []
        users_cursor = self.collection.find({"_id": {"$in": user_ids}})
        users = await _run_db_call(users_cursor.to_list, length=None)
        return users or []

    async def create_user(self, user_document: dict[str, Any]) -> dict[str, Any]:
        insert_result = await _run_db_call(self.collection.insert_one, user_document)
        inserted_id = getattr(insert_result, "inserted_id", None)
        if inserted_id is not None:
            user_document["_id"] = inserted_id
        return user_document

    async def update_user(self, user_id: Any, update_data: dict[str, Any]) -> None:
        await _run_db_call(
            self.collection.update_one,
            {"_id": user_id},
            {"$set": update_data},
        )

    async def append_refresh_token(self, user_id: Any, refresh_token_data: dict[str, Any]) -> None:
        await _run_db_call(
            self.collection.update_one,
            {"_id": user_id},
            {
                "$push": {"refresh_tokens": refresh_token_data},
                "$set": {"updated_at": refresh_token_data["created_at"]},
            },
        )

    async def revoke_refresh_token(self, user_id: Any, token_hash: str, revoked_at: Any) -> None:
        await _run_db_call(
            self.collection.update_one,
            {"_id": user_id, "refresh_tokens.token_hash": token_hash},
            {
                "$set": {
                    "refresh_tokens.$.revoked_at": revoked_at,
                    "updated_at": revoked_at,
                }
            },
        )

    async def mark_refresh_token_used(self, user_id: Any, token_hash: str, last_used_at: Any) -> None:
        await _run_db_call(
            self.collection.update_one,
            {"_id": user_id, "refresh_tokens.token_hash": token_hash},
            {
                "$set": {
                    "refresh_tokens.$.last_used_at": last_used_at,
                    "updated_at": last_used_at,
                }
            },
        )

    async def clear_expired_refresh_tokens(self, user_id: Any, now: Any) -> None:
        await _run_db_call(
            self.collection.update_one,
            {"_id": user_id},
            {
                "$pull": {
                    "refresh_tokens": {"expires_at": {"$lt": now}}
                }
            },
        )
        await _run_db_call(
            self.collection.update_one,
            {"_id": user_id},
            {
                "$pull": {
                    "refresh_tokens": {"revoked_at": {"$ne": None}}
                }
            },
        )
