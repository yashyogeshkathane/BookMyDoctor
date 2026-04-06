from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user_model import UserRole, UserStatus


class AdminUserListItem(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str = ""
    role: UserRole
    user_status: UserStatus
    created_at: datetime


class PaginatedAdminUsersResponse(BaseModel):
    items: list[AdminUserListItem]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class ApproveDoctorResponse(BaseModel):
    message: str
    user: AdminUserListItem
