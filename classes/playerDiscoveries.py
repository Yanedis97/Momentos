import random
from datetime import datetime, timedelta, timezone
from bson import ObjectId

class PlayerDiscoveries:
    def get_moment_discovery(db, player_id: str):

        progress_collection = db["player_progress"]
        discoveries_collection = db["player_discoveries"]
        moments_collection = db["moments"]

        # momentos jugados
        played = progress_collection.find({"player_id": player_id})
        played_ids = [p["moment_id"] for p in played]

        # momentos ya mostrados
        discovered = discoveries_collection.find({"player_id": player_id})
        discovered_ids = [d["moment_id"] for d in discovered]

        excluded_ids = played_ids + discovered_ids

        query = {}

        if excluded_ids:
            query["_id"] = {"$nin": [ObjectId(x) for x in excluded_ids]}

        moments = list(moments_collection.find(query))

        if not moments:
            return None

        moment = random.choice(moments)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=5)

        discoveries_collection.insert_one({
            "player_id": player_id,
            "moment_id": str(moment["_id"]),
            "shown_at": now,
            "expires_at": expires,
            "accepted": False
        })

        return {
            "moment_id": str(moment["_id"]),
            "title": moment.get("title"),
            "location": moment.get("location"),
            "expires_in": 300
        }
    
    def accept_moment(db, player_id: str, moment_id: str):

        discoveries_collection = db["player_discoveries"]

        discoveries_collection.update_one(
            {
                "player_id": player_id,
                "moment_id": moment_id
            },
            {
                "$set": {
                    "accepted": True
                }
            }
        )

        return {"status": "accepted"}