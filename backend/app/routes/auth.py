from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import authenticate_user, create_token, register_user

router = APIRouter()


@router.post('/api/auth/register', response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(payload.name, payload.email, payload.password, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": {"id": user['id'], "name": user['name'], "email": user['email']}}


@router.post('/api/auth/login', response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(payload.email, payload.password, db)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": {"id": user['id'], "name": user['name'], "email": user['email']}}

