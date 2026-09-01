from fastapi import APIRouter, HTTPException

from app.models.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import authenticate_user, create_token, register_user

router = APIRouter()


@router.post('/api/auth/register', response_model=AuthResponse)
def register(payload: RegisterRequest):
    try:
        user = register_user(payload.name, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": {"id": user['id'], "name": user['name'], "email": user['email']}}


@router.post('/api/auth/login', response_model=AuthResponse)
def login(payload: LoginRequest):
    try:
        user = authenticate_user(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": {"id": user['id'], "name": user['name'], "email": user['email']}}
