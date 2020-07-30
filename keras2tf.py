#!/usr/bin/env python

import os
import argparse

import tensorflow as tf
from keras import backend as K
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


def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = tf.graph_util.convert_variables_to_constants(
            session, input_graph_def, output_names, freeze_var_names)
        return frozen_graph


def main(args=None):
    K.set_learning_phase(0)
    args = parse_args(args)
    weights_name = args.input
    backbone = args.backbone

    dirname = os.path.dirname(weights_name)
    basename = os.path.basename(weights_name)
    fn, ext = os.path.splitext(basename)

    model = models.load_model(weights_name, backbone_name=backbone))
    frozen_graph = freeze_session(K.get_session(), output_names=[out.op.name for out in model.outputs])
    tf.train.write_graph(frozen_graph, dirname, f'{fn}.pb', as_text=False)
    print(f'weights saved: {dirname}')


if __name__ == '__main__':
    main()