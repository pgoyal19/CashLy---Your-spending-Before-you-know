import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "cashly-demo-secret")
JWT_ALGORITHM = "HS256"

USER_STORE = {}


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, hashed_password: str) -> bool:
    if ":" not in hashed_password:
        return False
    salt_hex, digest_hex = hashed_password.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()
    return hmac_compare(expected, digest_hex)


def hmac_compare(expected: str, actual: str) -> bool:
    return secrets_compare(expected, actual)


def secrets_compare(left: str, right: str) -> bool:
    return len(left) == len(right) and sum(a != b for a, b in zip(left, right)) == 0


def create_token(user_id: str, email: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": user_id, "email": email, "exp": expiry.timestamp()}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def register_user(name: str, email: str, password: str):
    if email in USER_STORE:
        raise ValueError("User already exists")
    user = {
        "id": f"user-{len(USER_STORE) + 1}",
        "name": name,
        "email": email,
        "password": hash_password(password),
    }
    USER_STORE[email] = user
    return user


def authenticate_user(email: str, password: str):
    user = USER_STORE.get(email)
    if not user:
        raise ValueError("Invalid credentials")
    if not verify_password(password, user["password"]):
        raise ValueError("Invalid credentials")
    return user
