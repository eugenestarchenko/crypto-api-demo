from fastapi import APIRouter
from .endpoints import health, currency

router = APIRouter()
router.include_router(health.router, tags=["Health"])
router.include_router(currency.router, tags=["Currency"])
