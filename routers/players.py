from fastapi import APIRouter, Depends, Body, HTTPException
from core.connection import get_db
from models.player import Player
from classes.players import PlayerService
from core.security import verify_token

router = APIRouter(prefix="/players", tags=["Players"], dependencies=[Depends(verify_token)])


@router.get("/")
def get_players():
    db = get_db()
    try:
        return PlayerService.get_players(db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{player_id}")
def get_player(player_id: str):
    db = get_db()
    try:
        return PlayerService.get_player(db, player_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/")
def create_player(player: Player = Body(...)):
    db = get_db()
    try:
        return PlayerService.create_player(db, player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{player_id}")
def update_player(player_id: str, item: dict = Body(...)):
    db = get_db()
    try:
        return PlayerService.update_player(db, player_id, item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
