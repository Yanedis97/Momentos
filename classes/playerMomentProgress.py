from datetime import datetime, timezone


class PlayerMomentProgress:

    @staticmethod
    def start_moment(db, player_id: str, moment_id: str):
        now = datetime.now(timezone.utc)

        moment = db.moments.find_one({"_id": moment_id})
        start_step = moment.get("meta", {}).get("start", "inicio")

        progress = {
            "player_id": player_id,
            "moment_id": moment_id,
            "status": "in_progress",
            "current_step": start_step,
            "steps_seen": [start_step],
            "flags": {},
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
    def validate_and_advance(
        db,
        player_id: str,
        moment_id: str,
        step: str,
        choice_next: str = None
    ):
        moment = db.moments.find_one({"_id": moment_id})

        if not moment:
            raise ValueError("Moment not found")

        states = moment.get("states", {})

        if step not in states:
            raise ValueError("Step not found")

        progress = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })
        
        start_step = moment.get("meta", {}).get("start", "inicio")

        if not progress:
            if step != start_step:
                raise ValueError(f"You must start from '{start_step}'")

            PlayerMomentProgress.start_moment(db, player_id, moment_id)

        else:
            current_step = progress["current_step"]

            if current_step not in states:
                start_step = moment.get("meta", {}).get("start", "inicio")

                PlayerMomentProgress._advance_step(
                    db,
                    player_id,
                    moment_id,
                    start_step
                )

                current_step = start_step
                
            current_state = states[current_step]

            state_type = current_state.get("type", "narrative")

            # Validar transición según tipo
            if state_type == "decision":
                choices = current_state.get("choices", [])

                selected_choice = None

                for c in choices:
                    if c["next"] == choice_next:
                        selected_choice = c
                        break

                if not selected_choice:
                    raise ValueError("Invalid choice")
                
                if "set" in selected_choice:
                    PlayerMomentProgress._apply_flags(
                        db,
                        player_id,
                        moment_id,
                        selected_choice["set"]
                    )
            else:
                expected_next = current_state.get("next")

                if expected_next and step not in [expected_next, current_step]:
                    raise ValueError("Invalid step flow")

            # avanzar progreso
            PlayerMomentProgress._advance_step(
                db,
                player_id,
                moment_id,
                step
            )

        # determinar si es último
        state = states[step]

        is_last = (
            state.get("next") is None and
            not state.get("choices")
        )

        if is_last:
            PlayerMomentProgress._advance_step(
                db,
                player_id,
                moment_id,
                step,
                "completed"
            )

        return is_last

    @staticmethod
    def _advance_step(db, player_id: str, moment_id: str, step: str, status: str ="in_progress"):

        now = datetime.now(timezone.utc)

        update = {
            "$set": {
                "current_step": step,
                "last_interaction_at": now,
                "status": status
            },
            "$addToSet": {
                "steps_seen": step
            }
        }

        db.player_progress.update_one(
            {"player_id": player_id, "moment_id": moment_id},
            update
        )

    @staticmethod
    def play_step(
        db,
        moment_id: str,
        player_id: str,
        step: str,
        choice_next: str = None
    ):
        moment = db.moments.find_one({"_id": moment_id})

        if not moment:
            raise ValueError("Moment not found")

        states = moment.get("states", {})

        if step not in states:
            raise ValueError("Step not found")

        is_last = PlayerMomentProgress.validate_and_advance(
            db,
            player_id,
            moment_id,
            step,
            choice_next
        )

        state = states[step]

        progress = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })

        flags = progress.get("flags", {})

        if "conditions" in state:
            if not PlayerMomentProgress._check_conditions(state["conditions"], flags):
                raise ValueError("Conditions not met")

        return {
            "moment_id": moment_id,
            "step": step,
            "type": state.get("type", "narrative"),
            "scene": state.get("scene", {
                "text": state.get("text", "")}),
            "autoNext": state.get("autoNext"),
            "duration": state.get("duration"),
            "choices": state.get("choices", []),
            "next_step": state.get("next"),
            "is_last": is_last,
            "flags": flags
        }

    def _check_conditions(conditions: list, flags: dict):
        if not conditions:
            return True

        for condition in conditions:
            key, expected = condition.split("==")
            key = key.strip()
            expected = expected.strip()

            if str(flags.get(key)) != expected:
                return False

        return True

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
    
    @staticmethod
    def _apply_flags(db, player_id, moment_id, new_flags: dict):
        progress = db.player_progress.find_one({
            "player_id": player_id,
            "moment_id": moment_id
        })

        current_flags = progress.get("flags", {})

        updated_flags = {**current_flags, **new_flags}

        db.player_progress.update_one(
            {"player_id": player_id, "moment_id": moment_id},
            {
                "$set": {"flags": updated_flags}
            }
        )