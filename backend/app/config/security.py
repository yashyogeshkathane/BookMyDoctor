import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config.settings import settings

try:
    import jwt
except ModuleNotFoundError:
    jwt = None


def _encode_token(
    subject: str,
    secret_key: str,
    expires_delta: timedelta,
    token_type: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    if jwt is None:
        raise RuntimeError("PyJWT is not installed. Install 'PyJWT' to create tokens.")

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": secrets.token_urlsafe(16),
    }
    if extra_claims:
        payload.update(extra_claims)

    expires_at = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expires_at
    return jwt.encode(payload, secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    return _encode_token(
        subject=subject,
        secret_key=settings.jwt_secret_key,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
        extra_claims=extra_claims,
    )


def create_refresh_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    return _encode_token(
        subject=subject,
        secret_key=settings.refresh_token_secret_key,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        token_type="refresh",
        extra_claims=extra_claims,
    )


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}:{derived_key.hex()}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_password_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False

    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(derived_key.hex(), hash_hex)


def generate_email_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_email_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(token: str, token_type: str = "access") -> dict[str, Any]:
    if jwt is None:
        raise RuntimeError("PyJWT is not installed. Install 'PyJWT' to decode tokens.")

    secret_key = (
        settings.jwt_secret_key
        if token_type == "access"
        else settings.refresh_token_secret_key
    )
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    if payload.get("type") != token_type:
        raise ValueError(f"Invalid token type. Expected {token_type}.")
    return payload
