from fastapi import APIRouter, HTTPException, File, UploadFile
from core.api_models.common import Result
from core.ml.retina import Model

model = Model()
model.load()

router = APIRouter()

@router.post("/infer", response_model=Result)
async def predict_on_image(image: UploadFile = File(...)) -> Result:
    if image.content_type.startswith('image/') is False:
        raise HTTPException(status_code=400, detail=f'File \'{image.filename}\' is not an image.')
    
    try:
        image_bytes = await image.read()
        predicts = await model.infer(in_data=image_bytes)
        return Result(objects=predicts)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))