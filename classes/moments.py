from fastapi import HTTPException
from datetime import datetime
from classes.playerProgress import PlayerMomentProgress

class MomentService:

    @staticmethod
    def get_moment(db, moment_id: str):
        moment = db.moments.find_one({"_id": moment_id})

        if moment is None:
            raise HTTPException(status_code=404, detail="Moment not found")

        moment["_id"] = str(moment["_id"])
        return moment

    @staticmethod
    def get_moments(db):
        moments = list(db.moments.find())

        if not moments:
            raise HTTPException(status_code=404, detail="No moments found")

        response = []
        for m in moments:
            response.append({
                "id": m["_id"],
                "title": m["title"],
                "year": m["year"],
                "suceso": m["states"]["suceso"]["text"]
            })

        return response

    @staticmethod
    def create_moment(db, moment):
        moment_dict = moment.model_dump()

        moment_dict["_id"] = (
            f"{moment.location.country.lower()}_"
            f"{moment.year}_"
            f"{moment.title.lower().replace(' ', '_')}"
        )

        existing = db.moments.find_one({"_id": moment_dict["_id"]})
        if existing:
            raise HTTPException(status_code=400, detail="Moment already exists")

        db.moments.insert_one(moment_dict)

        return {"message": "Moment created successfully"}

    @staticmethod
    def create_group_moments(db, list_moment: list):
        prepared = []

        for moment in list_moment:
            if "_id" not in moment:
                moment["_id"] = (
                    f"{moment['location']['country'].lower()}_"
                    f"{moment['year']}_"
                    f"{moment['title'].lower().replace(' ', '_')}"
                )

            prepared.append(moment)

        db.moments.insert_many(prepared)

        return {"message": "Moments created successfully"}

    @staticmethod
    def update_moment(db, moment_id: str, item: dict):
        result = db.moments.update_one(
            {"_id": moment_id},
            {"$set": item}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Moment not found")

        return {"message": "Moment updated successfully"}

    @staticmethod
    def play_step(db, moment_id: str, player_id: str, step: str):

        moment = db.moments.find_one({"_id": moment_id})

        if not moment:
            raise HTTPException(status_code=404, detail="Moment not found")

        steps_order = [
            "inicio",
            "contexto",
            "evento",
            "suceso",
            "reaccion",
            "dato_curioso"
        ]

        if step not in steps_order:
            raise HTTPException(status_code=400, detail="Invalid step")

        states = moment.get("states", {})

        if step not in states:
            raise HTTPException(status_code=400, detail="Step not found")

        current_index = steps_order.index(step)

        next_step = (
            steps_order[current_index + 1]
            if current_index < len(steps_order) - 1
            else None
        )

        is_last = next_step is None

        progress = PlayerMomentProgress.get_progress(db, player_id, moment_id)

        if not progress:
            if step != "inicio":
                raise HTTPException(
                    status_code=400,
                    detail="You must start from 'inicio'"
                )
            PlayerMomentProgress.start_moment(db, player_id, moment_id)
        else:
            current_step = progress["current_step"]
            current_index = steps_order.index(current_step)

            allowed_steps = [
                current_step,
                steps_order[current_index + 1]
                if current_index < len(steps_order) - 1
                else None
            ]

            if step not in allowed_steps:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid step order"
                )

        PlayerMomentProgress.advance_step(
            db,
            player_id,
            moment_id,
            step,
            is_last
        )

        return {
            "moment_id": moment_id,
            "step": step,
            "text": states[step]["text"],
            "next_step": next_step,
            "is_last": is_last
        }