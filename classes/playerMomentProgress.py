from datetime import datetime, timezone


class PlayerMomentProgress:

    STEPS_ORDER = [
        "inicio",
        "contexto",
        "evento",
        "suceso",
        "reaccion",
        "dato_curioso"
    ]

    @staticmethod
    def start_moment(db, player_id: str, moment_id: str):
        now = datetime.now(timezone.utc)

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

    @staticmethod
    def get_progress(db, player_id: str, moment_id: str):
        progress = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })

        if not progress:
            raise ValueError("Progress not found")

        return progress

    @staticmethod
    def validate_and_advance(db, player_id: str, moment_id: str, step: str):

        if step not in PlayerMomentProgress.STEPS_ORDER:
            raise ValueError("Invalid step")

        progress = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })

        if not progress:
            if step != "inicio":
                raise ValueError("You must start from 'inicio'")

            PlayerMomentProgress.start_moment(db, player_id, moment_id)
            current_index = 0

        else:
            current_step = progress["current_step"]
            current_index = PlayerMomentProgress.STEPS_ORDER.index(current_step)

            allowed_steps = [
                current_step,
                PlayerMomentProgress.STEPS_ORDER[current_index + 1]
                if current_index < len(PlayerMomentProgress.STEPS_ORDER) - 1
                else None
            ]

            if step not in allowed_steps:
                raise ValueError("Invalid step order")

            current_index = PlayerMomentProgress.STEPS_ORDER.index(step)

            PlayerMomentProgress._advance_step(
                db,
                player_id,
                moment_id,
                step,
                current_index
            )

        next_step = (
            PlayerMomentProgress.STEPS_ORDER[current_index + 1]
            if current_index < len(PlayerMomentProgress.STEPS_ORDER) - 1
            else None
        )

        is_last = next_step is None

        return is_last, next_step

    @staticmethod
    def _advance_step(db, player_id: str, moment_id: str, step: str, step_index: int):

        now = datetime.now(timezone.utc)
        is_last = step_index == len(PlayerMomentProgress.STEPS_ORDER) - 1

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

    @staticmethod
    def play_step(db, moment_id: str, player_id: str, step: str):

        moment = db.moments.find_one({"_id": moment_id})

        if not moment:
            raise ValueError("Moment not found")

        states = moment.get("states", {})

        if step not in states:
            raise ValueError("Step not found")

        is_last, next_step = PlayerMomentProgress.validate_and_advance(
            db,
            player_id,
            moment_id,
            step
        )

        return {
            "moment_id": moment_id,
            "step": step,
            "text": states[step]["text"],
            "next_step": next_step,
            "is_last": is_last
        }
    

    @staticmethod
    def get_player_moments_paginated(
        db,
        player_id: str,
        page: int = 1,
        limit: int = 10
    ):
        if page < 1 or limit < 1:
            raise ValueError("Invalid pagination values")

        skip = (page - 1) * limit

        query = {"player_id": player_id}

        total = db.player_progress.count_documents(query)

        cursor = (
            db.player_progress
            .find(query)
            .sort("last_interaction_at", -1)
            .skip(skip)
            .limit(limit)
        )

        results = []
        for doc in cursor:
            results.append({
                "moment_id": doc["moment_id"],
                "status": doc["status"],
                "current_step": doc["current_step"],
                "last_interaction_at": doc["last_interaction_at"],
                "completed_at": doc["completed_at"]
            })

        return {
            "player_id": player_id,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "data": results
        }
