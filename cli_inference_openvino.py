#!/usr/bin/env python

import os
import time
import argparse

import cv2
import numpy as np
from openvino.inference_engine import IENetwork, IECore
import json


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
        help='path to bin openVINO inference model',
        type=str,
        required=True
    )
    parser.add_argument(
        '--xml',
        help='path to xml model sheme',
        type=str,
        required=True
    )
    parser.add_argument(
        '--count',
        help='iference count',
        type=int,
        required=False,
        default=3
    )
    return parser.parse_args(args)


def decode_openvino_detections(detections, input_shape = (800, 1333)):
    """
    Converts openvino detections to understandable format

    Parameters:
    detections: Detections obtained from net.infer() method.
    input_shape: This is required to scale the bounding boxes coordinates passed.

    Returns:
    boxes: The bounding box coordinates representing (xmin, ymin, xmax, ymax)
    scores: The confidence of the detections
    labels: The class of the object detected

    """
    detections = detections[:,:,detections[:,:,:,2].argsort()[0][0][::-1],:] # sort detections on score
    labels = detections[:,:,:,1].astype(int)
    scores = detections[:,:,:,2]
    boxes = detections[:,:,:,(3,4,5,6)] # in decimal
    # rescale to pixel
    boxes[:,:,:,(0,2)] = boxes[:,:,:,(0,2)]*input_shape[1]
    boxes[:,:,:,(1,3)] = boxes[:,:,:,(1,3)]*input_shape[0]

    return boxes[0], scores[0], labels[0]

def compute_resize_scale(image_shape, min_side=800, max_side=1333):
    """ Compute an image scale such that the image size is constrained to min_side and max_side.

    Args
        min_side: The image's min side will be equal to min_side after resizing.
        max_side: If after resizing the image's max side is above max_side, resize until the max side is equal to max_side.

    Returns
        A resizing scale.
    """
    (rows, cols, _) = image_shape

    smallest_side = min(rows, cols)

    # rescale the image so the smallest side is min_side
    scale = min_side / smallest_side

    # check if the largest side is now greater than max_side, which can happen
    # when images have a large aspect ratio
    largest_side = max(rows, cols)
    if largest_side * scale > max_side:
        scale = max_side / largest_side

    return scale

def preprocess_image(x, mode='caffe'):
    """ Preprocess an image by subtracting the ImageNet mean.

    Args
        x: np.array of shape (None, None, 3) or (3, None, None).
        mode: One of "caffe" or "tf".
            - caffe: will zero-center each color channel with
                respect to the ImageNet dataset, without scaling.
            - tf: will scale pixels between -1 and 1, sample-wise.

    Returns
        The input with the ImageNet mean subtracted.
    """
    # mostly identical to "https://github.com/keras-team/keras-applications/blob/master/keras_applications/imagenet_utils.py"
    # except for converting RGB -> BGR since we assume BGR already

    # covert always to float32 to keep compatibility with opencv
    x = x.astype(np.float32)

    if mode == 'tf':
        x /= 127.5
        x -= 1.
    elif mode == 'caffe':
        x[..., 0] -= 103.939
        x[..., 1] -= 116.779
        x[..., 2] -= 123.68

    return x

def main(args=None):
    args=parse_args(args)

    model_xml = args.xml
    model_bin = args.bin
    img_fn = args.img
    predict_count = args.count
    
    print("initialize OpenVino...")
    OpenVinoIE = IECore()
    print("available devices: ", OpenVinoIE.available_devices)
    
    OpenVinoIE.set_config({"CPU_BIND_THREAD": "YES"}, "CPU")

    print("loading model...")
    net = IENetwork(model=model_xml, weights=model_bin)
    config = {}
    OutputLayer = next(iter(net.outputs))
    OpenVinoExecutable = OpenVinoIE.load_network(network=net, config=config, device_name="CPU")

    input_blob = 'input_1'
    net.batch_size = 1
    _, _, h, w = net.inputs[input_blob].shape
    print(f'model input shape: {net.inputs[input_blob].shape}')


    # load images
    image = cv2.imread(img_fn)
    if image.shape[:-1] != (h, w):
        print("image {} is resized from {} to {}".format(img_fn, image.shape[:-1], (h, w)))
        scale = compute_resize_scale(image.shape)
        image = cv2.resize(image, (w, h))
    image = preprocess_image(image)

    image = image.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    image = np.expand_dims(image, axis=0)
    labels_to_names = {0: 'Pedestrian'}

    print(f'make {predict_count} predictions:')

    for _ in range(0, predict_count):
        start_time = time.time()
        res = OpenVinoExecutable.infer(inputs={input_blob: image})
        print("\t{} s".format(time.time() - start_time))
    print("prepoocess image at {} s".format(time.time() - start_time))
    
    print("*"*20)
    boxes, scores, labels = decode_openvino_detections(res[OutputLayer])
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