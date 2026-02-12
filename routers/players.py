from fastapi import APIRouter, HTTPException, Body
from core.connection import get_db
from models.player import Player
from classes.players import PlayerService

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/{player_id}")
def get_player(player_id: str):
    db = get_db()
    return PlayerService.get_player(db, player_id)


@router.get("/")
def get_players():
    db = get_db()
    return PlayerService.get_players(db)


@router.post("/")
def create_player(player: Player = Body(...)):
    db = get_db()
    return PlayerService.create_player(db, player)


@router.put("/{player_id}")
def update_player(player_id: str, item: dict = Body(...)):
    db = get_db()
    return PlayerService.update_player(db, player_id, item)
