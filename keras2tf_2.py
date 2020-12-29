#!/usr/bin/env python

import os
import argparse
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

from keras_retinanet import models


def parse_args(args):
    parser = argparse.ArgumentParser(description='convert keras_retinanet model to tensorflow frozen graph')
    parser.add_argument(
        '--input', 
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
    return parser.parse_args(args)

def main(args=None):
    args = parse_args(args)
    weights_name = args.input
    backbone = args.backbone

    dirname = os.path.dirname(weights_name)
    basename = os.path.basename(weights_name)
    fn, ext = os.path.splitext(basename)

    model = models.load_model(weights_name, backbone_name=backbone)

    # Convert Keras model to ConcreteFunction
    full_model = tf.function(lambda input_1: model(input_1))
    full_model = full_model.get_concrete_function(
        tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))

    # Get frozen ConcreteFunction
    frozen_func = convert_variables_to_constants_v2(full_model)
    frozen_func.graph.as_graph_def()

    layers = [op.name for op in frozen_func.graph.get_operations()]

    print("Frozen model inputs: ")
    print(frozen_func.inputs)
    print("Frozen model outputs: ")
    print(frozen_func.outputs)

    # Save frozen graph to disk
    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                      logdir=dirname,
                      name=f"{fn}.pb",
                      as_text=False)
    print(f'weights saved: {dirname}')

if __name__ == '__main__':
    main()