from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from app.api.v1 import api_router
from app.config import settings
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/payment/success")
def payment_success(session_id: str = Query(None)):
    return {
        "message": "Payment successful! Your order will be processed.",
        "session_id": session_id,
    }


@app.get("/payment/cancel")
def payment_cancel():
    return {"message": "Payment cancelled. Your order is still pending."}
