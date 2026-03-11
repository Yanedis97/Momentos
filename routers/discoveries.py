from fastapi import APIRouter, HTTPException, Body, Query, Depends
from core.connection import get_db
from classes.playerDiscoveries import playerDiscoveries
from models.PlayerDiscoveries import PlayerAccepted
from core.security import verify_token

router = APIRouter(prefix="/discoveries", tags=["Player Discoveries"], dependencies=[Depends(verify_token)])


@router.post("/accept")
def accept_moment(accepted: PlayerAccepted = Body(...)):
    db = get_db()
    player_id = accepted.player_id
    moment_id = accepted.moment_id

    try:
        return playerDiscoveries.accept_moment(db, player_id, moment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{player_id}")
def get_moment_discovery(
    player_id: str
):
    db = get_db() 
    try:
        return playerDiscoveries.get_moment_discovery(
        db,
        player_id
    )  
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))