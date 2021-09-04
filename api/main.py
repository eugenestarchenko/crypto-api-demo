from fastapi import FastAPI
from api.v1.routers import router
import os

app = FastAPI(
    title="Coinbase cryptocurrency API",
    description="API to track current currencies prices",
)
app.include_router(router, prefix="/v1")


@app.get("/")
def read_root():
    return {"Hello": "Crypto API Demo ✨"}
