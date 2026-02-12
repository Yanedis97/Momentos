from fastapi import FastAPI
from classes import moments, playerProgress

app = FastAPI()

app.include_router(moments.router)
app.include_router(playerProgress.router)