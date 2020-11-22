import tensorflow as tf
import numpy as np
from keras_retinanet import models
from keras_retinanet.utils.image import preprocess_image, resize_image
from core.config import WorkerConfig, get_config
from core.ml.enum import InferTypeEnum
import os
import cv2
import time

class Model:
    def __init__(self) -> None:
        config = get_config()
        assert os.path.isfile(config.weights), f"no such file: {config.weights}"
        assert config.backbone != None, "backbone is None"
        assert config.labels != None, "labels is none"
        self.config = config
        self.model = None
    
    def load(self) -> None:
        if self.config.infer_type == InferTypeEnum.gpu:
            self._setup_gpu(0)
        elif self.config.infer_type == InferTypeEnum.cpu:
            self._setup_gpu(-1)
        else:
            raise Exception(f"unsuported infer_type {self.config.infer_type}")

        self.model = models.load_model(self.config.weights, backbone_name=self.config.backbone)
        #TODO: logging
        print(
            "ML model is doads\n" +
            "\tfreamwork: tensorflow\n" +
            f"\tweights: {self.config.weights}\n" +
            f"\tbackbone: {self.config.backbone}\n" +
            f"\tinference type: {self.config.infer_type}\n" +
            f"\timage min side: {self.config.min_side}\n" +
            f"\timage max side: {self.config.max_side}\n", flush=True 
            )

    def infer(self, in_data: bytes) -> dict:
        # pre-processing
        img_bytes = np.asarray(bytearray(in_data), dtype=np.uint8)
        image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
        image, scale = resize_image(image, min_side=self.config.min_side, max_side=self.config.max_side)
        image = preprocess_image(image)
        
        # inference
        start_time = time.time()
        boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(image, axis=0))
        print("done in {} s".format(time.time() - start_time), flush=True)

        # post-processing
        boxes /= scale
        objects = []
        result = {
            'objects': objects
        }
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            if score < 0.5:
                break
            b = np.array(box.astype(int)).astype(int)
            # x1 y1 x2 y2
            obj = {
                'label': self.config.labels[label],
                'xmin': b[0],
                'ymin': b[1],
                'xmax': b[2],
                'ymax': b[3],
                'score': score
            }
            objects.append(obj)
        return result


    def _setup_gpu(self, gpu_id: int) -> None:
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
                # TODO: logging
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                raise Exception(f"unable to setup gpu: {e}")