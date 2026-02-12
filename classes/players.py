from fastapi import APIRouter, HTTPException, Body
from core.connection import get_db
from models.player import Player

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/{player_id}")
def get_player(player_id: str):
    db = get_db()
    try:
        player = db.players.find_one({"_id": player_id})
    except:
        raise HTTPException(status_code=400, detail = "Invalid player ID")
    
    if player is None:
        raise HTTPException(status_code=404, detail = "Player not found")
        
    return player

@router.get("/")
def get_players():
    db = get_db()
    try:
        players_cursor= db.players.find()
        players = list(players_cursor)
   
    except:
        raise HTTPException(status_code=400, detail = "Query error")

    if not players:
        raise HTTPException(status_code=404, detail = "No players found")
        
    return players

@router.post("/")
def create_player(player: Player = Body(...)):
    db = get_db()
    player_dict = player.model_dump(by_alias=True, exclude_none=True)

    if "_id" not in player_dict:
        player_dict["_id"] = player.username.lower().replace(" ", "_")

    if db.players.find_one({"_id": player_dict["_id"]}):
        raise HTTPException(status_code=400, detail="Player already exists")

    db.players.insert_one(player_dict)

    return {"message": "Player created successfully", "id": player_dict["_id"]}


@router.put("/{player_id}")
def update_player(player_id: str, item: dict = Body(...)):
    db = get_db()
    myquery = {"_id": player_id}
    newitem = {"$set":item}
    
    result = db.players.update_one(myquery, newitem)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Player not found")

    return {"message": "Player updated successfully"}
