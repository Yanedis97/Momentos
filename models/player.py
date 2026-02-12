from typing import Optional, Field
from pydantic import BaseModel
from datetime import datetime, timezone


class Preferences(BaseModel):
    show_paused_first: bool

class Profile(BaseModel):
    language: str
    experience_level: str
    preferences: Preferences

class Player(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    status: str = "active"
    profile: Profile