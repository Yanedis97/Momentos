import random
from datetime import datetime, timedelta, timezone

class PlayerDiscoveries:
    def get_moment_discovery(db, player_id: str):

        progress_collection = db["player_progress"]
        discoveries_collection = db["player_discoveries"]
        moments_collection = db["moments"]

        # momentos jugados
        played = progress_collection.find({"player_id": player_id})
        played_ids = [p["moment_id"] for p in played]

        # momentos ya mostrados
        now = datetime.now(timezone.utc)
        discovered = discoveries_collection.find({
            "player_id": player_id,
            "$or": [
                {"accepted": True}
            ]
        })
        discovered_ids = [d["moment_id"] for d in discovered]
        
        excluded_ids = played_ids + discovered_ids

        query = {}

        if excluded_ids:
            query["_id"] = {"$nin": excluded_ids}

        moments = list(moments_collection.find(query))
        if not moments:
            return {
                    "error": False,
                    "message": "No hay momentos disponibles para mostrar",
                    "data": None
                }

        moment = random.choice(moments)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=5)

        discoveries_collection.update_one(
            {
                "player_id": player_id,
                "moment_id": str(moment["_id"]),
                "accepted": False
            },
            {
                "$set": {
                    "shown_at": now,
                    "expires_at": expires,
                }
            },
            upsert=True
        )

        return {
            "moment_id": str(moment["_id"]),
            "title": moment.get("title"),
            "location": moment.get("location"),
            "expires_in": 300
        }
    
    def accept_moment(db, player_id: str, moment_id: str):
        discoveries_collection = db["player_discoveries"]

        now = datetime.now(timezone.utc)

        result = discoveries_collection.update_one(
            {
                "player_id": player_id,
                "moment_id": moment_id,
                "accepted": False
            },
            {
                "$set": {
                    "accepted": True,
                    "accepted_at": now
                }
            }
        )

        if result.matched_count == 0:
            return {
                "error": True,
                "message": "No se encontró el momento o ya fue aceptado/expirado"
            }

        return {
            "error": False,
            "message": "Momento aceptado correctamente"
        }