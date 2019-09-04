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
from PIL import Image
from io import BytesIO
import base64
import argparse
import sys
import os
import numpy as np
import time
import json
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status': "server is running"}), 200


@app.route('/image', methods=['POST'])
def predict_image():
    if not request.json or not 'data' in request.json:
        abort(400)
    
    caption = run_detection_image(model, labels_to_names, request.json['data'])
    return caption, 200


def run_detection_image(model, labels_to_names, data):
    print("start predict {}")
    with graph.as_default():
        imgdata = base64.b64decode(data)
        npImage = np.asarray(Image.open(BytesIO(imgdata)).convert('RGB'))
        image = npImage[:, :, ::-1].copy()

        # copy to draw on
        draw = image
        draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

        # preprocess image for network
        image = preprocess_image(image)
        image, scale = resize_image(image)

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
              'ynax': str(b[3])
            }
            objects.append(obj)
            #caption += "output= {} {} {} {} {} {:.3f}\n".format(b[0], b[1], b[2], b[3], labels_to_names[label], score)
        reaponse_json = json.dumps(reaponse)
        print("done {}", reaponse_json)
        return reaponse_json

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
    return model, labels_to_names

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Evaluation script for a RetinaNet network.')
    parser.add_argument('--model',              help='Path to RetinaNet model.', default=os.path.join('snapshots', 'resnet50_liza_alert_v1_interface.h5'))
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    load_model(args)
    print('model loaded')
    app.run(debug=False, host='0.0.0.0', port=5000)    

if __name__ == '__main__':
    main()