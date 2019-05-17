import keras
# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import argparse
import sys
import os
import numpy as np
import time

import tensorflow as tf

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)


def run_detection_image(model, labels_to_names, filepath):
    image = read_image_bgr(filepath)

    # copy to draw on
    draw = image.copy()
    draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

    # preprocess image for network
    image = preprocess_image(image)
    image, scale = resize_image(image)

    # process image
    start = time.time()
    boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

    # correct for image scale
    boxes /= scale
    caption = ""

    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < 0.5:
            break
        b = np.array(box.astype(int)).astype(int)
        # x1 y1 x2 y2
        caption += "output= {} {} {} {} {} {:.3f}\n".format(b[0], b[1], b[2], b[3], labels_to_names[label], score)
    return caption

def main(args=None):
    # parse arguments
    #if args is None:
    #    args = sys.argv[1:]
    args = parse_args(args)

    # use this environment flag to change which GPU to use
    #os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    # set the modified tf session as backend in keras
    keras.backend.tensorflow_backend.set_session(get_session())
    model_path = args.model
    # load retinanet model
    model = models.load_model(model_path, backbone_name='resnet50')
    # load label to names mapping for visualization purposes
    labels_to_names = {0: 'Pedestrian'}
    print(run_detection_image(model, labels_to_names, args.image))

def parse_args(args):
    """ Parse the arguments.
    """
    parser     = argparse.ArgumentParser(description='Evaluation script for a RetinaNet network.')

    parser.add_argument('--model',              help='Path to RetinaNet model.', default=os.path.join('snapshots', 'resnet50_liza_alert_v1_interface.h5'))
    parser.add_argument('--image',              help='Path to image.', default='examples/235.jpg')

    return parser.parse_args(args)

if __name__ == '__main__':
    main()