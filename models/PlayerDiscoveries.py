from pydantic import BaseModel
from datetime import datetime

class PlayerDiscoveries(BaseModel):
    player_id: str
    moment_id: str
    shown_at: datetime
    expires_at: datetime
    accepted: bool

class PlayerAccepted(BaseModel):
    player_id: str
    moment_id: str
