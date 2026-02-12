from fastapi import APIRouter, HTTPException
from core.connection import get_db
from classes.playerProgress import PlayerMomentProgress

router = APIRouter(prefix="/progress", tags=["Player Progress"])


@router.post("/{player_id}/{moment_id}/start")
def start_moment(player_id: str, moment_id: str):
    db = get_db()

    try:
        return PlayerMomentProgress.start_moment(db, player_id, moment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{player_id}/{moment_id}")
def get_progress(player_id: str, moment_id: str):
    db = get_db()

    try:
        return PlayerMomentProgress.get_progress(db, player_id, moment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{player_id}/{moment_id}/advance")
def advance_step(player_id: str, moment_id: str, step: str, is_last: bool):
    db = get_db()

    try:
        return PlayerMomentProgress.advance_step(
            db, player_id, moment_id, step, is_last
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{player_id}/{moment_id}/pause")
def pause_moment(player_id: str, moment_id: str):
    db = get_db()

    try:
        return PlayerMomentProgress.pause_moment(db, player_id, moment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
