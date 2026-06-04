from pymongo.errors import BulkWriteError


class MomentService:

    @staticmethod
    def get_moment(db, moment_id: str):
        moment = db.moments.find_one({"_id": moment_id})

        if moment is None:
            raise ValueError("Moment not found")

        moment["_id"] = str(moment["_id"])
        return moment

    @staticmethod
    def get_moments(db):
        moments = list(db.moments.find())

        if not moments:
            raise ValueError("No moments found")

        response = []
        for m in moments:
            response.append({
                "id": m["_id"],
                "title": m.get("title"),
                "year": m.get("timeline", {}).get("year"),
                "suceso": m.get("states", {}).get("suceso", {}).get("scene", {}).get("text")
            })

        return response

    @staticmethod
    def create_moment(db, moment):
        moment_dict = moment.model_dump()

        moment_dict["_id"] = (
            f"{moment.location.country.lower()}_"
            f"{moment.timeline.year}_"
            f"{moment.title.lower().replace(' ', '_')}"
        )

        existing = db.moments.find_one({"_id": moment_dict["_id"]})
        if existing:
            raise ValueError("Moment already exists")

        db.moments.insert_one(moment_dict)

        return {"message": "Moment created successfully"}

    @staticmethod
    def create_group_moments(db, list_moment: list):
        prepared = []

        for moment in list_moment:
            if "_id" not in moment:
                moment["_id"] = (
                    f"{moment['location']['country'].lower()}_"
                    f"{moment['timeline']['year']}_"
                    f"{moment['title'].lower().replace(' ', '_')}"
                )

            prepared.append(moment)

        try:
            db.moments.insert_many(prepared, ordered=False)
        except BulkWriteError as e:
            inserted = e.details.get("nInserted", 0)
            errors = len(e.details.get("writeErrors", []))
            return {
                "message": f"Insercion parcial: {inserted} creados, {errors} duplicados omitidos"
            }

        return {"message": "Moments created successfully"}

    @staticmethod
    def update_moment(db, moment_id: str, item: dict):
        result = db.moments.update_one(
            {"_id": moment_id},
            {"$set": item}
        )

        if result.matched_count == 0:
            raise ValueError("Moment not found")

        return {"message": "Moment updated successfully"}
