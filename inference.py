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
from typing import NamedTuple, List

app = Flask(__name__)

class Prediction:
    def __init__(self, 
                xmin: int,
                ymin: int, 
                xmax: int,
                ymax: int,
                score: float,
                label: str) -> None:

        self.xmin: int = xmin
        self.ymin: int = ymin
        self.xmax: int = xmax
        self.ymax: int = ymax
        self.score: float = score
        self.label: str = label

def run_detection_image(data):
    start_time = time.time()
    imgdata = pybase64.b64decode(data)
    file_bytes = np.asarray(bytearray(imgdata), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    # preprocess image for network
    image, scale = resize_image(image, min_side=2100, max_side=2100)
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
    result_bboxes: List[Prediction] = []

    # filter detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        if score < 0.15:
            break
        
        b = np.array(box.astype(int)).astype(int)
        # x0 y0 x1 y1
        tagret = Prediction(
            xmin=b[0],
            ymin=b[1],
            xmax=b[2],
            ymax=b[3],
            score=score,
            label=labels_to_names[label]
        )
        is_merged = False

        for res in result_bboxes:
            if res.label != tagret.label:
                continue

            if res.xmin <= tagret.xmin and res.xmax >= tagret.xmin:
                res.xmax = max(res.xmax, tagret.xmax)
                is_merged = True
            if res.xmin <= tagret.xmax and res.xmax >= tagret.xmax:
                res.xmin = min(res.xmin, tagret.xmin)
                is_merged = True
            if res.ymin <= tagret.ymin and res.ymax >= tagret.ymin:
                res.ymax = max(res.ymax, tagret.ymax)
                is_merged = True
            if res.ymin <= tagret.ymax and res.ymax >= tagret.ymax:
                res.ymin = min(res.ymin, tagret.ymin)
                is_merged = True
            if tagret.xmin <= res.xmin and tagret.xmax >= res.xmax:
                res.xmax = max(res.xmax, tagret.xmax)
                res.xmin = min(res.xmin, tagret.xmin)
                is_merged = True
            if tagret.ymin <= res.ymin and tagret.ymax >= res.ymax:
                res.ymax = max(res.ymax, tagret.ymax)
                res.ymin = min(res.ymin, tagret.ymin)
                is_merged = True
            
            if is_merged:
                res.score = max(res.score, tagret.score)
        
        if not is_merged:
            result_bboxes.append(tagret)

    # visualize detections
    for res in result_bboxes:
        obj = {
          'name': res.label,
          'score': str(res.score),
          'xmin': str(res.xmin),
          'ymin': str(res.ymin),
          'xmax': str(res.xmax),
          'ymax': str(res.ymax)
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
    parser.add_argument('--model', help='Path to RetinaNet model.', default=os.path.join('snapshots', 'lacmus_v5_interface.h5'))
    parser.add_argument('--gpu', help='Visile gpu device. Set to -1 if CPU', type=int, default=0)
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    load_model(args)
    print('model loaded')
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
