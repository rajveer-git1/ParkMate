from fastapi import FastAPI

from backend import models
from backend.database import Base, engine
from backend.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ParkMate API")

app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "ParkMate API is running"}