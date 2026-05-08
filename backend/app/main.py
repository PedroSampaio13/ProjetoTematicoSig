from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.db import test_connection

app = FastAPI(title="SIG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API SIG a funcionar"}

@app.get("/test")
def test():
    return {"message": "backend ok"}

@app.get("/db-test")
def db_test():
    version = test_connection()

    return {
        "message": "Ligação à base de dados OK",
        "postgres_version": version
    }