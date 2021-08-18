#!/usr/bin/env python
import tensorflow as tf
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image, compute_resize_scale
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
import cv2
import argparse
import numpy as np
import time


def parse_args(args):
    parser = argparse.ArgumentParser(description='convert model')
    parser.add_argument(
        '--img',
        help='path to image',
        type=str,
        required=True
    )
    parser.add_argument(
        '--bin',
        help='path to h5 keras inference model',
        type=str,
        required=True
    )
    parser.add_argument(
        '--backbone',
        help='backbone name',
        type=str,
        required=False,
        default='resnet50'
    )
    parser.add_argument(
        '--count',
        help='iference count',
        type=int,
        required=False,
        default=1
    )
    parser.add_argument(
        '--height',
        help='iference count',
        type=int,
        required=False,
        default=2100
    )
    parser.add_argument(
        '--width',
        help='iference count',
        type=int,
        required=False,
        default=2100
    )
    parser.add_argument(
        '--gpu',
        help='use gpu',
        action='store_true',
        required=False,
    )
    return parser.parse_args(args)

def create_model(backbone_name, num_classes=1):
    backbone_factory = models.backbone(backbone_name)
    model = backbone_factory.retinanet(num_classes)
    return models.convert_model(model)

def setup_gpu(gpu_id: int):
    if gpu_id == -1:
        tf.config.experimental.set_visible_devices([], 'GPU')
        return

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.experimental.set_virtual_device_configuration(
                gpus[gpu_id],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)])
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            print(e)

def main(args=None):
    args=parse_args(args)

    model_bin = args.bin
    img_fn = args.img
    predict_count = args.count
    backbone = args.backbone
    min_side = min(args.height, args.width)
    max_side = max(args.height, args.width)

    print("loading model...")
    if args.gpu:
        setup_gpu(0)

    model = models.load_model(model_bin, backbone_name=backbone)

    print(f'model input shape: {model.inputs[0].shape}')

    start_time = time.time()

    image = cv2.imread(img_fn)
    image, scale = resize_image(image, min_side=min_side, max_side=max_side)
    image = preprocess_image(image)
    print("prepoocess image at {} s".format(time.time() - start_time))

    labels_to_names = {0: 'Pedestrian'}

    print(f'make {predict_count} predictions:')
    for _ in range(0, predict_count):
        start_time = time.time()
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
        print("\t{} s".format(time.time() - start_time))

    
    print("*"*20)
    print('bboxes:', boxes.shape)
    print('scores:', scores.shape)
    print('labels:', labels.shape)

    boxes /= scale

    objects_count = 0

    print("*"*20)
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < 0.5:
            break
        b = np.array(box.astype(int)).astype(int)
        # x1 y1 x2 y2
        print(f'{labels_to_names[label]}:')
        print(f'\tscore: {score}')
        print(f'\tbox: {b[0]} {b[1]} {b[2]} {b[3]}')
        objects_count = objects_count + 1
    print(f'found objects: {objects_count}')


if __name__ == '__main__':
    main()