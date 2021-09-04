from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter()


@router.get("/health")
async def get_health(request: Request):
    """
    Retrieve health.
    """
    return {"health": "ok"}
