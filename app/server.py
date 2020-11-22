from fastapi import FastAPI
from api.v0.routes.api import router as api_router
from core.config import get_config

def get_application() -> FastAPI:
    project_name = get_config().project_name
    debug = get_config().debug
    version = get_config().version
    prefix = get_config().api_prefix

    application = FastAPI(title=project_name, debug=debug, version=version)
    application.include_router(api_router, prefix=prefix)
    #TODO: logging
    print(f"init application with\n\tprefix: {prefix}\n\tversion: {version}", flush=True)
    return application

app = get_application()