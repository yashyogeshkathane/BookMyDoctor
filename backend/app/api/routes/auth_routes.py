from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.auth_schema import (
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterResponse,
    UserLoginRequest,
    UserRegisterRequest,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegisterRequest) -> RegisterResponse:
    try:
        return await auth_service.register_user(payload)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating your account. Please try again."
        )
        


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(payload: VerifyEmailRequest) -> VerifyEmailResponse:
    try:
        return await auth_service.verify_email(payload.token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while verifying your email. Please try again."
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(payload: UserLoginRequest) -> LoginResponse:
    try:
        return await auth_service.login_user(payload)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to sign you in right now. Please try again shortly."
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(payload: RefreshTokenRequest) -> LoginResponse:
    try:
        return await auth_service.refresh_access_token(payload.refresh_token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Your session could not be refreshed. Please sign in again."
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout_user(payload: RefreshTokenRequest) -> LogoutResponse:
    try:
        return await auth_service.logout_user(payload.refresh_token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to log out right now. Please try again."
        )

@router.post("/login-oauth")
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        login_response = await auth_service.login_user(
            UserLoginRequest(
                email=form_data.username,
                password=form_data.password,
            )
        )
        return {
            "access_token": login_response.access_token,
            "refresh_token": login_response.refresh_token,
            "token_type": login_response.token_type,
            "user": login_response.user,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to sign you in right now. Please try again shortly.",
        )
