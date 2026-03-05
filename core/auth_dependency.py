from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from bson import ObjectId
from core.connection import get_db

SECRET_KEY = "CHANGE_THIS_IN_ENV"
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)  # tu dependencia de conexión
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        player_id = payload.get("sub")

        if not player_id:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    player = db.players.find_one({"_id": ObjectId(player_id)})

    if not player:
        raise HTTPException(status_code=401, detail="Player not found")

    return player