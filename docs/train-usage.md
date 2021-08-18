# Keras RetinaNet on Liza Alert Drone Data Set [![Build Status](https://travis-ci.org/fizyr/keras-retinanet.svg?branch=master)](https://travis-ci.org/fizyr/keras-retinanet)

Keras implementation of RetinaNet object detection as described in [Focal Loss for Dense Object Detection](https://arxiv.org/abs/1708.02002).

This code is borrowed from Keras Implementation of this model at https://github.com/fizyr/keras-retinanet and updated to run on Liza Alert Drone Dataset (LADD)

## Installation
1. Install:
   - tensorflow >= 2.4.2
   - setuptools
   - opencv-python
   - our keras-resnet fork: `pip install git+https://github.com/lacmus-foundation/keras-resnet.git`
2. Clone this repository.
3. In the repository, execute `pip install .`.
4. To run the code directly from the cloned repository, you need to run `python setup.py build_ext --inplace` to compile Cython code first.
5. Optionally, install `pycocotools` if you want to train / test on the MS COCO dataset by running `pip install git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI`.


## Training on custom data set (added by Priyanka Dwivedi, Georgy Perevozchikov)

*First step is to create pre-trained backbone model using [Standford Drone Dataset (SDD)](http://cvgl.stanford.edu/projects/uav_data)*


For training on a custom dataset, a CSV file can be used as a way to pass the data.
See [below](train-usage.md#annotations-format) for more details on the format of these CSV files.


To train using your CSV, run:

```
keras_retinanet/bin/train.py --weights snapshots/resnet50_coco_best_v2.1.0.h5 csv ../data/SDD-CSV/train_annotations.csv labels.csv --val-annotations ../data/SDD-CSV/val_annotations.csv
```
Here: 
* --weights: Path to the weights for initializing training
* csv indicates retinanet is trained on a custom data set
* train_annotations.csv is path to training annotations
* labels.csv are the labels in the format class_name, class_id with 0 reserved for background class
* --val_annotations: Path to validation annotations 

You can find the model resnet50_base_best.h5 trained this way in Assets [here](https://github.com/lizaalert/lacmus/releases/tag/0.1.0).

*Second step is to train on LADD dataset and fine-tuning model*

To train using your Pascal VOC, run:
```
keras_retinanet/bin/train.py --weights snapshots/resnet50_base_best.h5 --freeze-backbone --config config.ini pascal ../data/LADD
```

*Running directly from `RetinaNet` folder in the repository*

Here: 
* pascal indicates retinanet is trained on a dataset of Pascal VOC format 
* --config config.ini: configuration file with anchor parameters

If your dataset is small, you can also use the `--freeze-backbone argument` to freeze the backbone layers.

You can find more arguments directly in parse_args function of [train.py](../keras_retinanet/bin/train.py) file.

A model trained on a LADD dataset can be found [here](https://github.com/lizaalert/lacmus/releases/tag/0.1.1).

### Training Set
I uploaded the images used for training and validation to the yandex disk link below. Please download the same:
<https://yadi.sk/d/4Hz_1qpiNbHhpQ>

### Annotations format
The CSV file with annotations should contain one annotation per line.
Images with multiple bounding boxes should use one row per bounding box.
Note that indexing for pixel values starts at 0.
The expected format of each line is:
```
path/to/image.jpg,x1,y1,x2,y2,class_name
```

**Labels format**

The class name to ID mapping file should contain one mapping per line.
Each line should use the following format:
```
class_name,id
```

## Evaluating Results (added by Priyanka Dwivedi and Georgy Perevozchikov)

To calculate mean average precision on the validation set, please run

```
keras_retinanet/bin/evaluate.py csv val_annotations.csv labels.csv snapshots/resnet50_csv_31_interface.h5
```

or for Pascal VOC

```
keras_retinanet/bin/evaluate.py pascal ../data/LADD snapshots/resnet50_pascal_06.h5  --convert-model
```

Here we pass the val_annotations, labels and path to the trained weights.

**Note:** If you were using --config config.ini argument when training the model and pass option --convert-model when evaluating, you should provide the same configuaration file, otherwise you can encounter error "InvalidArgumentError: 
Incompatible shapes" like [in this issue](https://github.com/priya-dwivedi/aerial_pedestrian_detection/issues/3).  


## Running Inference on Images and Videos (added by Priyanka Dwivedi and Georgy Perevozchikov)

To run inference on the trained model, first step is to convert the trained model to a format that can be used by inference. The command for this is:

```
keras_retinanet/bin/convert_model.py snapshots/resnet50_pascal_08.h5 snapshots/resnet50_pascal_08_inference.h5 
```

Here first path is the path to the trained model and the second would be the path to the converted inference model

I created two notebooks from the original code that can be used to run inference on images and on videos.

The notebooks are:
* [RetinaNet/ResNet50RetinaNet-Image.ipynb](../ResNet50RetinaNet-Image.ipynb) : For inference on a batch of images
* [RetinaNet/ResNet50RetinaNet-Video.ipynb](../ResNet50RetinaNet-Video.ipynb) : For inference on a video

