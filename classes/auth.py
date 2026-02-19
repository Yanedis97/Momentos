import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from models.auth import LoginRequest


SECRET_KEY = "CHANGE_THIS_IN_ENV"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class AuthService:

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def login(db, login_data: LoginRequest):

        player = db.players.find_one({"email": login_data.email})

        if not player:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if "password_hash" not in player:
            raise HTTPException(status_code=400, detail="Password not configured")

        is_valid = AuthService.verify_password(
            login_data.password,
            player["password_hash"]
        )

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = AuthService.create_access_token({
            "sub": player["_id"]
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "player_id": player["_id"]
        }