from fastapi import FastAPI

app = FastAPI(title="ParkMate API")


@app.get("/")
def read_root():
    return {"message": "ParkMate API is running"}