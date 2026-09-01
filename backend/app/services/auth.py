import hashlib
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from sqlalchemy.orm import Session

from app.models.database import User

JWT_SECRET = os.getenv("JWT_SECRET", "cashly-demo-secret")
JWT_ALGORITHM = "HS256"


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


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def register_user(name: str, email: str, password: str, db: Session):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("User already exists")
    
    user_id = f"user-{uuid4().hex[:8]}"
    user = User(
        id=user_id,
        name=name,
        email=email,
        password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid credentials")
    if not verify_password(password, user.password):
        raise ValueError("Invalid credentials")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


def get_user_by_id(user_id: str, db: Session):
    return db.query(User).filter(User.id == user_id).first()

