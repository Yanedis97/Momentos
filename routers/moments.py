from fastapi import APIRouter, HTTPException, Body
from core.connection import get_db
from models.moment import Moment
from classes.moments import MomentService

router = APIRouter(prefix="/moments", tags=["Moments"])


@router.get("/{moment_id}")
def get_moment(moment_id: str):
    db = get_db()
    try:
        return MomentService.get_moment(db, moment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def get_moments():
    db = get_db()
    return MomentService.get_moments(db)


@router.post("/")
def create_moment(moment: Moment = Body(...)):
    db = get_db()
    return MomentService.create_moment(db, moment)


@router.post("/create_all")
def create_group_moments(list_moment: list = Body(...)):
    db = get_db()
    return MomentService.create_group_moments(db, list_moment)


@router.put("/{moment_id}")
def update_moment(moment_id: str, item: dict = Body(...)):
    db = get_db()
    return MomentService.update_moment(db, moment_id, item)


@router.get("/{moment_id}/play")
def play_step(moment_id: str, player_id: str, step: str):
    db = get_db()
    return MomentService.play_step(db, moment_id, player_id, step)
