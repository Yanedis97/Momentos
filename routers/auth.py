from fastapi import APIRouter
from core.connection import get_db
from models.auth import LoginRequest
from classes.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(login_data: LoginRequest):
    db = get_db()
    return AuthService.login(db, login_data)
