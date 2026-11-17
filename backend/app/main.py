from fastapi import FastAPI

from app import models  # noqa: F401  (loads the models so the tables are registered)
from app.api import bookings, lots, users
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(users.router)
app.include_router(lots.router)
app.include_router(bookings.router)


@app.get("/")
def read_root():
    return {"message": "ParkMate API is running"}