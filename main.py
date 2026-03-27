from fastapi import FastAPI
from routers import moments, progress, players, auth, discoveries
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.include_router(moments.router)
app.include_router(progress.router)
app.include_router(players.router)
app.include_router(auth.router)
app.include_router(discoveries.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)