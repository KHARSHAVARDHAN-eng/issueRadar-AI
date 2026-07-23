import base64
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from cryptography.fernet import Fernet

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """Retrieve or derive a valid 32-byte url-safe base64 Fernet key."""
    raw_key = settings.ENCRYPTION_KEY.encode()
    try:
        return Fernet(raw_key)
    except Exception:
        digest = hashlib.sha256(raw_key).digest()
        derived_key = base64.urlsafe_b64encode(digest)
        return Fernet(derived_key)


def encrypt_token(token: str) -> str:
    """Encrypt a sensitive token string using Fernet (AES-128-CBC)."""
    if not token:
        return ""
    fernet = _get_fernet()
    encrypted_bytes = fernet.encrypt(token.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a Fernet-encrypted token string."""
    if not encrypted_token:
        return ""
    try:
        fernet = _get_fernet()
        decrypted_bytes = fernet.decrypt(encrypted_token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        return ""


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT refresh token with extended expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)

    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_refresh_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a JWT refresh token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token for user sessions."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a signed JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"Invalid or expired JWT token: {e}")
        return None
