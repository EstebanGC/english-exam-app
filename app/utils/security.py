from datetime import datetime, timedelta, timezone
import os


import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError



password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain password against an Argon2 hash.
    """
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is not configured"
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for an authenticated user.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    """
    Decode and validate a JWT access token.

    Returns:
        int: authenticated user ID
    """

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError("Token does not contain a user ID")

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError) as e:
        raise ValueError("Invalid or expired token") from e