### Tool for generation of new dataset images

#### How it works
- cuts all target images from existing dataset;
- transforms crops (at the moment only random rotation is implemented);
- puts crops on new backgrounds;
- generates Pascal VOC-style annotations.

#### Inputs

Before running: update **config.cfg** with your data.

Folders: 
- **DATASET_PATH** - location of existing dataset;
- **BACKGROUNDS_FOLDER_NAME** - name of folder with new backgroungs, the folder shall be located in a folder with existing dataset;
- **AUGMENTED_FOLDER_NAME** - name of folder for outputs, the folder also shall be located in a folder with existing dataset;

Cropping details:

Targets being cropped with some padding and pixels for smooth transition. 

Example: if the 
- target image is 50x50 pixels,
- padding is 10% of image W and H,
- transition area is 25 pixels at each side of image, 

then crop will have a size: 
**H = W = (50 + 50x0,1  + 50x0,1 + 25 + 25) = 110 px**

Related variables:
- **PADDING_WIDTH** - **percentage** of target image H and W to pad,
- **INPAINT_PIXELS_WIDTH** - width of smooth transition area.



#### Outputs

All outputs are located in **AUGMENTED_FOLDER_NAME**:

- **JPEGImages** - folder with resulting images,
- **Annotations** - folder with xml annotations files,
- **Targets** - crops of targets.

<img src = "https://github.com/lacmus-foundation/lacmus/blob/master/data_utils/ImgGenerator/imgs/in_forest.PNG" width=600>

<img src = "https://github.com/lacmus-foundation/lacmus/blob/master/data_utils/ImgGenerator/imgs/on_snow.PNG" width=600>

<img src = "https://github.com/lacmus-foundation/lacmus/blob/master/data_utils/ImgGenerator/imgs/in_soup.PNG" width=300> <img src = "https://github.com/lacmus-foundation/lacmus/blob/master/data_utils/ImgGenerator/imgs/in_soup2.PNG" width=300>
