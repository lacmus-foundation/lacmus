from fastapi import APIRouter, HTTPException, Request, Response
from core.config import get_config
from core.api_models.common import Pong


router = APIRouter()

@router.get("/ping", response_model=Pong)
async def root() -> Pong:
    project_name = get_config().project_name
    version = get_config().version
    return Pong(pong=f"{project_name}, version {version}")