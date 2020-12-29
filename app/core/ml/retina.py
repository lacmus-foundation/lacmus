import tensorflow as tf
import numpy as np
from keras_retinanet import models
from keras_retinanet.utils.image import preprocess_image, resize_image
from core.config import WorkerConfig, get_config
from core.ml.enum import InferTypeEnum
from core.api_models.common import Prediction
from typing import List
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

    async def infer(self, in_data: bytes) -> List[Prediction]:
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
                label=self.config.labels[label]
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
        return result_bboxes


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