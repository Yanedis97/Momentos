from fastapi import FastAPI
from routers import moments, progress, players

app = FastAPI()

app.include_router(moments.router)
app.include_router(progress.router)
app.include_router(players.router)