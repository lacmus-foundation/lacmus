import keras
# import keras_retinanet
import tensorflow as tf
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

def run_detection_image(model, image):
    with graph.as_default():
        # preprocess image for network
        image = preprocess_image(image)
        image, scale = resize_image(image)

        # process image
        start = time.time()
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

        # correct for image scale
        boxes /= scale
        return boxes, scores, labels

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.Session(config=config)
    return session

def load_model(args):
    keras.backend.tensorflow_backend.set_session(get_session())
    model_path = args.model
    # load retinanet model
    global model
    model = models.load_model(model_path, backbone_name='resnet50')
    # load label to names mapping for visualization purposes
    global labels_to_names
    labels_to_names = {0: 'Pedestrian'}
    global graph
    graph = tf.get_default_graph()
    print('model loaded')
    return model, labels_to_names

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Evaluation script for a RetinaNet network.')
    parser.add_argument('--model', help='Path to RetinaNet model.', default=os.path.join('snapshots', 'resnet50_liza_alert_v1_interface.h5'))
    parser.add_argument('--capture', help='capture Id', default=0, type=int)
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    load_model(args)
    cap = cv2.VideoCapture(args.capture)
    while(cap.isOpened()):
        ret, frame = cap.read()

        draw = frame.copy()
        draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

        boxes, scores, labels = run_detection_image(model, frame)

        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            # scores are sorted so we can break
            if score < 0.5:
                break

            color = label_color(label)

            b = box.astype(int)
            draw_box(draw, b, color=color)

            caption = "{} {:.3f}".format(labels_to_names[label], score)
            draw_caption(draw, b, caption)

        # Display the resulting frame
        resized_image = cv2.resize(frame, (1280, 820))
        cv2.imshow('Video', resized_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    main()
