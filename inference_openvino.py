from openvino.inference_engine import IENetwork, IECore
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

def resize_image(img, min_side=800, max_side=1333):
    """ Resize an image such that the size is constrained to min_side and max_side.

    Args
        min_side: The image's min side will be equal to min_side after resizing.
        max_side: If after resizing the image's max side is above max_side, resize until the max side is equal to max_side.

    Returns
        A resized image.
    """
    # compute scale to resize the image
    scale = compute_resize_scale(img.shape, min_side=min_side, max_side=max_side)

    # resize the image with the computed scale
    img = cv2.resize(img, None, fx=scale, fy=scale)

    return img, scale

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

def create_blank(image, w, h, color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in BGR"""
    r_image = np.zeros((h, w, 3), np.uint8)
    r_image[:] = color
    r_image[:image.shape[0],:image.shape[1],:image.shape[2]] = image
    return r_image

@app.route('/')
def index():
    return jsonify({'status': "server is running"}), 200


@app.route('/image', methods=['POST'])
def predict_image():
    if not request.json or not 'data' in request.json:
        abort(400)
    
    caption = run_detection_image(OpenVinoExecutable, InputLayer, OutputLayer, h, w, labels_to_names, request.json['data'])
    return caption, 200


def run_detection_image(OpenVinoExecutable, InputLayer, OutputLayer, h, w, labels_to_names, data):
    print("start predict...")
    start_time = time.time()
    imgdata = pybase64.b64decode(data)
    file_bytes = np.asarray(bytearray(imgdata), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    image, scale = resize_image(image)
    image = create_blank(image, w, h)
    image = preprocess_image(image)
    image = image.transpose((2, 0, 1))
    image = np.expand_dims(image, axis=0)
    print("preprocess in {} s".format(time.time() - start_time), flush=True)

    res = OpenVinoExecutable.infer(inputs={InputLayer: image})
    boxes, scores, labels = decode_openvino_detections(res[OutputLayer])
    boxes /= scale

    objects = []
    reaponse = {
        'objects': objects
    }
    
    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < 0.4:
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

def load_model(args):
    global OpenVinoExecutable
    global InputLayer
    global OutputLayer
    global w
    global h
    global labels_to_names

    model_xml = args.xml
    model_bin = args.bin

    OpenVinoIE = IECore()
    OpenVinoIE.set_config({"CPU_BIND_THREAD": "YES"}, "CPU")
    net = IENetwork(model=model_xml, weights=model_bin)
    config = {}
    InputLayer = 'input_1'
    OutputLayer = next(iter(net.outputs))
    OpenVinoExecutable = OpenVinoIE.load_network(network=net, config=config, device_name="CPU")
    net.batch_size = 1
    _, _, h, w = net.inputs[InputLayer].shape
    labels_to_names = {0: 'Pedestrian'}
    return OpenVinoExecutable, InputLayer, OutputLayer, h, w, labels_to_names

def parse_args(args):
    """ Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Evaluation script for a RetinaNet network.')
    parser.add_argument(
        '--bin',
        help='path to bin openVINO inference model',
        type=str,
        default=os.path.join('snapshots', 'resnet50_liza_alert_v1_interface.bin')
    )
    parser.add_argument(
        '--xml',
        help='path to xml model sheme',
        type=str,
        default=os.path.join('snapshots', 'resnet50_liza_alert_v1_interface.xml')
    )
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    load_model(args)
    print('model loaded')
    app.run(debug=False, host='0.0.0.0', port=5000)    

if __name__ == '__main__':
    main()
