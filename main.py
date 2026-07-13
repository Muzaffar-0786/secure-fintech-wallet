# main.py

from fastapi import FastAPI

from database import create_tables
from auth import router as auth_router
from wallet import router as wallet_router
from rewards import router as rewards_router


app = FastAPI(
    title="Secure FinTech Wallet API",
    version="1.0.0",
    description="Production Ready MVP using FastAPI"
)

create_tables()


app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(rewards_router)


@app.get("/")
def root():
    return {
        "message": "Secure FinTech Wallet API is running.",
        "version": "1.0.0",
        "status": "OK"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected"
    }
