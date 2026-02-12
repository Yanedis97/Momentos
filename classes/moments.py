from fastapi import APIRouter, HTTPException, Body
from core.connection import get_db
from models.moment import Moment
from classes.playerProgress import get_progress, start_progress, update_progress

router = APIRouter(prefix="/moments", tags=["Moments"])

@router.get("/{moment_id}")
def get_moment(moment_id: str):
    db = get_db()
    try:
        moment = db.moments.find_one({"_id": moment_id})
    except:
        raise HTTPException(status_code=400, detail = "Invalid moment ID")
    
    if moment is None:
        raise HTTPException(status_code=404, detail = "Moment not found")
        
    return moment

@router.get("/")
def get_moments():
    db = get_db()
    try:
        moments_cursor= db.moments.find()
        moments = list(moments_cursor)
   
    except:
        raise HTTPException(status_code=400, detail = "Query error")

    if not moments:
        raise HTTPException(status_code=404, detail = "No moments found")
        
    response = []
    for m in moments:
        response.append({
            "id": m["_id"],
            "title": m["title"],
            "year": m["year"],
            "suceso": m["states"]["suceso"]["text"]
        })

    return response


@router.post("/")
def create_moment(moment: Moment = Body(...)):
    db = get_db()
    moment_dict = moment.model_dump()

    moment_dict["_id"] = (
        f"{moment.location.country.lower()}_"
        f"{moment.year}_"
        f"{moment.title.lower().replace(' ', '_')}"
    )

    db.moments.insert_one(moment_dict)

    return {"message": "Moment created successfully"}

@router.post("/create_all")
def create_group_moments(list_moment: list = Body(...)):
    db = get_db()
    prepared_moments = []

    for moment in list_moment:
        if "_id" not in moment:
            moment["_id"] = (
                f"{moment['location']['country'].lower()}_"
                f"{moment['year']}_"
                f"{moment['title'].lower().replace(' ', '_')}"
            )

        prepared_moments.append(moment)

    db.moments.insert_many(prepared_moments)
        
    return {"message": "Moment created successfully"}

@router.put("/{moment_id}")
def update_moment(moment_id: str, item: dict = Body(...)):
    db = get_db()
    myquery = {"_id": moment_id}
    newitem = {"$set":item}
    
    result = db.moments.update_one(myquery, newitem)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Moment not found")

    return {"message": "Moment updated successfully"}

@router.get("/{moment_id}/play")
def play_step(moment_id: str, player_id: str, step: str):
    db = get_db()

    try:
        moment = db.moments.find_one({"_id": moment_id})
    except:
        raise HTTPException(status_code=400, detail = "Invalid moment ID")
    
    if moment is None:
        raise HTTPException(status_code=404, detail = "Moment not found")
    
    steps_order = [
        "inicio",
        "contexto",
        "evento",
        "suceso",
        "reaccion",
        "dato_curioso"
    ]
    
    if step not in steps_order:
        raise HTTPException(status_code=400, detail = "Invalid step")
    
    states = moment.get("states",{})

    if step not in states:
        raise HTTPException(status_code=400, detail = "Step not found")

    current_index = steps_order.index(step)

    next_step = (
        steps_order[current_index + 1]
        if current_index < len(steps_order) - 1
        else None
    )

    is_last = next_step is None

    progress = get_progress(player_id, moment_id)

    if not progress:
        if step != "inicio":
            raise HTTPException(
                status_code=400,
                detail="You must start from 'inicio'"
            )
        start_progress(player_id, moment_id)
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

    update_progress(player_id, moment_id, step, is_last)


    data = {
        "moment_id": moment_id,
        "step": step,
        "text": states[step]["text"],
        "next_step": next_step,
        "is_last": is_last
    }

    return data