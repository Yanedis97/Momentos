from fastapi import APIRouter, HTTPException, Body, Query
from core.connection import get_db
from classes.playerMomentProgress import PlayerMomentProgress

router = APIRouter(prefix="/progress", tags=["Player Progress"])


@router.get("/{player_id}/{moment_id}")
def get_progress(player_id: str, moment_id: str):
    db = get_db()

    try:
        return PlayerMomentProgress.get_progress(db, player_id, moment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/play")
def play_step(
    moment_id: str = Body(...), 
    player_id: str = Body(...), 
    step: str = Body(...)
    ):
    
    db = get_db()
    try:
        return PlayerMomentProgress.play_step(db, moment_id, player_id, step)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{player_id}")
def get_player_moments(
    player_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    db = get_db() 
    try:
        return PlayerMomentProgress.get_player_moments_paginated(
        db,
        player_id,
        page,
        limit
    )  
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))