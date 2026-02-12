from pydantic import BaseModel

class Location(BaseModel):
    country: str
    city: str

class TextBlock(BaseModel):
    text: str

class States(BaseModel):
    inicio: TextBlock
    contexto: TextBlock
    evento: TextBlock
    suceso: TextBlock
    reaccion: TextBlock
    dato_curioso: TextBlock

class Observables(BaseModel):
    deportistas: list[str]
    publico: bool

class Moment(BaseModel):
    title: str
    location: Location
    year: int
    states: States
    observables: Observables