from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Literal


class Location(BaseModel):
    country: str
    city: str
    lat: float
    lng: float


class Choice(BaseModel):
    id: str
    label: str
    next: str
    set: Optional[Dict[str, Any]] = None


class State(BaseModel):
    type: Optional[Literal[
        "scene",
        "decision",
        "pause",
        "reveal"
    ]] = "scene"
    text: str
    next: Optional[str] = None
    choices: Optional[List[Choice]] = None


class Observables(BaseModel):
    deportistas: List[str]
    publico: bool


class Timeline(BaseModel):
    year: int
    date: Optional[str] = None
    label: Optional[str] = None


class Moment(BaseModel):
    title: str
    location: Location
    year: int
    timeline: Optional[Timeline] = None
    meta: Optional[Dict[str, Any]]
    states: Dict[str, State]
    observables: Observables