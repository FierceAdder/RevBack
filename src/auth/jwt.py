"""JWT token generation, validation, and password/API key hashing."""

from datetime import datetime, timezone, timedelta
import hashlib
import secrets
from typing import Optional, Dict, Any

import jwt
import bcrypt

from src.config import settings


def hash_password(password: str) -> str:
    """Hashes plain password using direct bcrypt."""
    pw_bytes = password[:72].encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed password using bcrypt."""
    if not hashed_password:
        return False
    try:
        pw_bytes = plain_password[:72].encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates signed JWT token with claims and expiration timestamp."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "revback-auth",
    })
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token signature and expiration."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="revback-auth",
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def hash_api_key(raw_key: str) -> str:
    """Computes SHA-256 hash of API key for secure database storage."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key(prefix: str = "rzb_live_") -> tuple[str, str, str]:
    """Generates a high-entropy API key.
    
    Returns:
        (raw_key, key_hash, key_prefix)
    """
    token = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{token}"
    key_hash = hash_api_key(raw_key)
    key_prefix = raw_key[:12]
    return raw_key, key_hash, key_prefix
