from fastapi import APIRouter
from api.v0.routes import ping
from api.v0.routes import predict

router = APIRouter()

router.include_router(ping.router, tags=["ping"])
router.include_router(predict.router, tags=["predict"])