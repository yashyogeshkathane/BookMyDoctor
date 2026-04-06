from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_admin
from app.schemas.admin_schema import ApproveDoctorResponse, PaginatedAdminUsersResponse
from app.schemas.auth_schema import AdminCreateRequest, AuthUserResponse
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/admins", tags=["Admins"])
auth_service = AuthService()
admin_service = AdminService()


@router.post("", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    payload: AdminCreateRequest,
    _: dict = Depends(get_current_admin),
) -> AuthUserResponse:
    try:
        return await auth_service.create_admin_by_admin(payload)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the admin account. Please try again.",
        )


@router.get("/doctors/pending", response_model=PaginatedAdminUsersResponse)
async def list_pending_doctors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=6, ge=1, le=50),
    _: dict = Depends(get_current_admin),
) -> PaginatedAdminUsersResponse:
    try:
        return await admin_service.list_pending_doctors(page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load pending doctors right now. Please try again.",
        )


@router.post("/doctors/{user_id}/approve", response_model=ApproveDoctorResponse)
async def approve_doctor(
    user_id: str,
    _: dict = Depends(get_current_admin),
) -> ApproveDoctorResponse:
    try:
        return await admin_service.approve_doctor(user_id=user_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to approve this doctor right now. Please try again.",
        )
