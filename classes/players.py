from fastapi import HTTPException


class PlayerService:

    @staticmethod
    def get_player(db, player_id: str):
        player = db.players.find_one({"_id": player_id})

        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")

        player["_id"] = str(player["_id"])
        return player

    @staticmethod
    def get_players(db):
        players = list(db.players.find())

        if not players:
            raise HTTPException(status_code=404, detail="No players found")

        for p in players:
            p["_id"] = str(p["_id"])

        return players

    @staticmethod
    def create_player(db, player):
        player_dict = player.model_dump(by_alias=True, exclude_none=True)

        if "_id" not in player_dict:
            player_dict["_id"] = (
                player.username.lower()
                .replace(" ", "_")
            )

        existing = db.players.find_one({"_id": player_dict["_id"]})

        if existing:
            raise HTTPException(status_code=400, detail="Player already exists")

        db.players.insert_one(player_dict)

        return {
            "message": "Player created successfully",
            "id": player_dict["_id"]
        }

    @staticmethod
    def update_player(db, player_id: str, item: dict):
        result = db.players.update_one(
            {"_id": player_id},
            {"$set": item}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Player not found")

        return {"message": "Player updated successfully"}
