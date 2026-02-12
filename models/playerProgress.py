from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PlayerMomentProgress(BaseModel):
    player_id: str
    moment_id: str

    status: str  # not_started | in_progress | paused | completed

    current_step: Optional[str] = None

    steps_seen: List[str] = Field(default_factory=list)

    started_at: datetime
    last_interaction_at: datetime
    completed_at: Optional[datetime] = None
