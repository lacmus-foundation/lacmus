"""
Copyright 2017-2018 Fizyr (https://fizyr.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import configparser
import numpy as np
import keras
from ..utils.anchors import AnchorParameters


def read_config_file(config_path):
    config = configparser.ConfigParser()

    with open(config_path, 'r') as file:
        config.read_file(file)

    assert 'anchor_parameters' in config, \
        "Malformed config file. Verify that it contains the anchor_parameters section."

    config_keys = set(config['anchor_parameters'])
    default_keys = set(AnchorParameters.default.__dict__.keys())

    assert config_keys <= default_keys, \
        "Malformed config file. These keys are not valid: {}".format(config_keys - default_keys)

    return config


def parse_anchor_parameters(config):
    ratios  = np.array(list(map(float, config['anchor_parameters']['ratios'].split(' '))), keras.backend.floatx())
    scales  = np.array(list(map(float, config['anchor_parameters']['scales'].split(' '))), keras.backend.floatx())
    sizes   = list(map(int, config['anchor_parameters']['sizes'].split(' ')))
    strides = list(map(int, config['anchor_parameters']['strides'].split(' ')))

    return AnchorParameters(sizes, strides, ratios, scales)


def parse_random_transform_parameters(config):
    kwargs = dict()
    kwargs['min_rotation'] = float(config['random_transform_parameters']['min_rotation'])
    kwargs['max_rotation'] = float(config['random_transform_parameters']['max_rotation'])
    kwargs['min_translation'] = tuple(map(float, config['random_transform_parameters']['min_translation'].split()))
    kwargs['max_translation'] = tuple(map(float, config['random_transform_parameters']['max_translation'].split()))
    kwargs['min_shear'] = float(config['random_transform_parameters']['min_shear'])
    kwargs['max_shear'] = float(config['random_transform_parameters']['max_shear'])
    kwargs['min_scaling'] = tuple(map(float, config['random_transform_parameters']['min_scaling'].split()))
    kwargs['max_scaling'] = tuple(map(float, config['random_transform_parameters']['max_scaling'].split()))
    kwargs['flip_x_chance'] = float(config['random_transform_parameters']['flip_x_chance'])
    kwargs['flip_y_chance'] = float(config['random_transform_parameters']['flip_y_chance'])

    return kwargs


def parse_visual_effect_parameters(config):
    kwargs = dict()
    kwargs['contrast_range'] = tuple(map(float, config['visual_effect_parameters']['contrast_range'].split()))
    kwargs['brightness_range'] = tuple(map(float, config['visual_effect_parameters']['brightness_range'].split()))
    kwargs['hue_range'] = tuple(map(float, config['visual_effect_parameters']['hue_range'].split()))
    kwargs['saturation_range'] = tuple(map(float, config['visual_effect_parameters']['saturation_range'].split()))

    return kwargs