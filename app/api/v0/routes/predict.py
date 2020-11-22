from fastapi import APIRouter, HTTPException, File, UploadFile
from core.api_models.common import Object, Result
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
        predicts = model.infer(in_data=image_bytes)
        result = Result(objects=[])
        for predict in predicts['objects']:
            obj = Object(
                label = predict['label'],
                xmax = predict['xmax'],
                xmin = predict['xmin'],
                ymax = predict['ymax'],
                ymin = predict['ymin'],
                score = predict['score']
            )    
            result.objects.append(obj)
        return result
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))