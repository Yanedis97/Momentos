from datetime import datetime, timezone


class PlayerMomentProgress:

    @staticmethod
    def start_moment(db, player_id: str, moment_id: str):

        now = datetime.now(timezone.utc)

        existing = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })

        if existing:
            raise ValueError("Progress already exists")

        progress = {
            "player_id": player_id,
            "moment_id": moment_id,
            "status": "in_progress",
            "current_step": "inicio",
            "steps_seen": ["inicio"],
            "started_at": now,
            "last_interaction_at": now,
            "completed_at": None
        }

        db.player_progress.insert_one(progress)

        return {"message": "Moment started"}


    @staticmethod
    def get_progress(db, player_id: str, moment_id: str):

        progress = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })

        if not progress:
            raise ValueError("Progress not found")

        progress["_id"] = str(progress["_id"])

        return progress


    @staticmethod
    def advance_step(db, player_id: str, moment_id: str, step: str, is_last: bool):

        now = datetime.now(timezone.utc)

        update = {
            "$set": {
                "current_step": step,
                "last_interaction_at": now,
                "status": "completed" if is_last else "in_progress"
            },
            "$addToSet": {
                "steps_seen": step
            }
        }

        if is_last:
            update["$set"]["completed_at"] = now

        result = db.player_progress.update_one(
            {"player_id": player_id, "moment_id": moment_id},
            update
        )

        if result.matched_count == 0:
            raise ValueError("Progress not found")

        return {"message": "Progress updated"}


    @staticmethod
    def pause_moment(db, player_id: str, moment_id: str):

        now = datetime.now(timezone.utc)

        result = db.player_progress.update_one(
            {"player_id": player_id, "moment_id": moment_id},
            {
                "$set": {
                    "status": "paused",
                    "last_interaction_at": now
                }
            }
        )

        if result.matched_count == 0:
            raise ValueError("Progress not found")

        return {"message": "Moment paused"}
