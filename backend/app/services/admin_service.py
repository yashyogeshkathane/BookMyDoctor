from datetime import datetime

from fastapi import HTTPException, status

from app.core.logger import get_logger
from app.models.base_model import ObjectId
from app.models.user_model import UserRole, UserStatus
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin_schema import (
    AdminUserListItem,
    ApproveDoctorResponse,
    PaginatedAdminUsersResponse,
)

logger = get_logger("service.admin")


class AdminService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.doctor_repository = DoctorRepository()

    @staticmethod
    def _map_user(user: dict) -> AdminUserListItem:
        return AdminUserListItem(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            phone=user.get("phone") or "",
            role=user["role"],
            user_status=user.get("user_status") or UserStatus.ACTIVE.value,
            created_at=user["created_at"],
        )

    async def list_pending_doctors(self, *, page: int, page_size: int) -> PaginatedAdminUsersResponse:
        logger.debug("Listing pending doctors: page=%d page_size=%d", page, page_size)
        filters = {
            "role": UserRole.DOCTOR.value,
            "user_status": UserStatus.PENDING_APPROVAL.value,
        }
        total = await self.user_repository.count_by_filters(filters)
        users = await self.user_repository.list_by_filters(
            filters,
            skip=(page - 1) * page_size,
            limit=page_size,
        )
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return PaginatedAdminUsersResponse(
            items=[self._map_user(user) for user in users],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )

    async def approve_doctor(self, *, user_id: str) -> ApproveDoctorResponse:
        logger.info("Doctor approval request: user_id=%s", user_id)

        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id.")

        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if user.get("role") != UserRole.DOCTOR.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only doctor accounts can be approved here.",
            )

        if user.get("user_status") != UserStatus.PENDING_APPROVAL.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This doctor is not waiting for approval.",
            )

        now = datetime.utcnow()
        await self.user_repository.update_user(
            user["_id"],
            {"user_status": UserStatus.ACTIVE.value, "updated_at": now},
        )
        await self.doctor_repository.update_by_user_id(
            user["_id"],
            {"updated_at": now, "approved_at": now},
        )

        updated_user = await self.user_repository.find_by_id(user["_id"])
        logger.info("Doctor approved: user_id=%s email=%s", user_id, user.get("email"))
        return ApproveDoctorResponse(
            message="Doctor approved successfully. They can now sign in.",
            user=self._map_user(updated_user or user),
        )
