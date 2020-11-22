from typing import List
from functools import lru_cache
from pydantic import BaseSettings
from core.ml.enum import InferTypeEnum

# https://github.com/tiangolo/fastapi/issues/508#issuecomment-532360198
class WorkerConfig(BaseSettings):
    project_name: str = "Lacmus ml worker"
    api_prefix: str = "/api/v2"
    version: str = "2.0.0"
    debug: bool = False

    weights: str = "../snapshotes/lacmus_v5_interface.h5"
    min_side: int = 2100
    max_side: int = 2100
    backbone: str = "resnet50"
    labels: dict = {0: 'Pedestrian'}
    infer_type: InferTypeEnum = InferTypeEnum.cpu   

    class Config:
        env_prefix = ""
        env_file = '.env'
        env_file_encoding = 'utf-8'

@lru_cache()
def get_config() -> WorkerConfig:
    return WorkerConfig()