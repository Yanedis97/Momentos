from fastapi import APIRouter, HTTPException, Body, Query, Depends
from core.connection import get_db
from classes.playerDiscoveries import PlayerDiscoveries
from models.PlayerDiscoveries import PlayerAccepted
from core.security import verify_token

router = APIRouter(prefix="/discoveries", tags=["Player Discoveries"], dependencies=[Depends(verify_token)])


@router.get("/{player_id}")
def get_moment_discovery(
    player_id: str
):
    db = get_db() 
    try:
        return PlayerDiscoveries.get_moment_discovery(
        db,
        player_id
    )  
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))