### Cropping tool for dataset images
Before running **bboxCropper.py**: update **config.cfg** with your data.


#### Inputs
Dataset, located at **DATASET_PATH**.


#### Outputs
- creates folders **CROPS_FOLDER_NAME**, **FRAMES_FOLDER_NAME**, **MASKS_FOLDER_NAME** in dataset folder.
- crops square of **CROP_SIZE*****CROP_SIZE** around bbox center on the image, with random shift, and saves it to **CROPS_FOLDER_NAME** folder.
- cuts out bbox content from this crop, saves it to **FRAMES_FOLDER_NAME** folder.
- creates binary mask of the size of the crop, with True pixels under bbox and all other zeros, saves it to **MASKS_FOLDER_NAME** folder.

#### About masks
- by default, mask pixels are True in places where image inpainting required, others are False. For mask inversion: set INVERT_MASKS in cfg file.

![Example](https://github.com/lacmus-foundation/lacmus/blob/master/data_utils/bboxCropper/screenshot.PNG)
