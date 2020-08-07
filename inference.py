import keras
# import keras_retinanet
import tensorflow as tf
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image, compute_resize_scale
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
# import miscellaneous modules
import cv2
from io import BytesIO
import pybase64
import argparse
import sys
import os
import numpy as np
import time
import json
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

def run_detection_image(data):
    start_time = time.time()
    imgdata = pybase64.b64decode(data)
    file_bytes = np.asarray(bytearray(imgdata), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    # preprocess image for network
    image, scale = resize_image(image)
    image = preprocess_image(image)
    print("preprocess in {} s".format(time.time() - start_time), flush=True)
    # process image
    boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
    # correct for image scale
    boxes /= scale
    objects = []
    reaponse = {
      'objects': objects
    }
    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < 0.5:
            break
        b = np.array(box.astype(int)).astype(int)
        # x1 y1 x2 y2
        obj = {
          'name': labels_to_names[label],
          'score': str(score),
          'xmin': str(b[0]),
          'ymin': str(b[1]),
          'xmax': str(b[2]),
          'ymax': str(b[3])
        }
        objects.append(obj)
    reaponse_json = json.dumps(reaponse)
    print("done in {} s".format(time.time() - start_time), flush=True)
    return reaponse_json


@app.route('/')
def index():
    return jsonify({'status': "server is running"}), 200


@app.route('/image', methods=['POST'])
def predict_image():
    if not request.json or not 'data' in request.json:
        abort(400)
    
    caption = run_detection_image(request.json['data'])
    return caption, 200

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

def load_model(args):
    global model
    global labels_to_names

    setup_gpu(args.gpu)
    model = models.load_model(args.model, backbone_name='resnet50')
    labels_to_names = {0: 'Pedestrian'}
    return model, labels_to_names

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Evaluation script for a RetinaNet network.')
    parser.add_argument('--model', help='Path to RetinaNet model.', default=os.path.join('snapshots', 'resnet50_liza_alert_v1_interface.h5'))
    parser.add_argument('--gpu', help='Visile gpu device. Set to -1 if CPU', type=int, default=0)
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    load_model(args)
    print('model loaded')
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
