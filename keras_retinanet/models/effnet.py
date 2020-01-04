''' 
https://github.com/lacmus-foundation/lacmus
Copyright (C) 2019-2020 lacmus-foundation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

import keras
from keras.utils import get_file

from . import retinanet
from . import Backbone
import efficientnet.keras as effnet


class EfficientNetBackbone(Backbone):
    """ Describes backbone information and provides utility functions.
    """

    def __init__(self, backbone):
        super(EfficientNetBackbone, self).__init__(backbone)
        self.preprocess_image_func = None

    def retinanet(self, *args, **kwargs):
        """ Returns a retinanet model using the correct backbone.
        """
        return effnet_retinanet(*args, backbone=self.backbone, **kwargs)

    def download_imagenet(self):
        """ Downloads ImageNet weights and returns path to weights file.
        """
        from efficientnet.model import BASE_WEIGHTS_PATH
        from efficientnet.model import WEIGHTS_HASHES

        model_name = 'efficientnet-b' + self.backbone[-1]
        file_name = model_name + '_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5'
        file_hash = WEIGHTS_HASHES[model_name][1]
        weights_path = get_file(file_name, BASE_WEIGHTS_PATH + file_name, cache_subdir='models', file_hash=file_hash)
        return weights_path

    def validate(self):
        """ Checks whether the backbone string is correct.
        """
        allowed_backbones = ['EfficientNetB0', 'EfficientNetB1', 'EfficientNetB2', 'EfficientNetB3', 'EfficientNetB4',
                             'EfficientNetB5', 'EfficientNetB6', 'EfficientNetB7']
        backbone = self.backbone.split('_')[0]

        if backbone not in allowed_backbones:
            raise ValueError('Backbone (\'{}\') not in allowed backbones ({}).'.format(backbone, allowed_backbones))

    def preprocess_image(self, inputs):
        """ Takes as input an image and prepares it for being passed through the network.
        """
        return effnet.preprocess_input(inputs)


def effnet_retinanet(num_classes, backbone='EfficientNetB0', inputs=None, modifier=None, **kwargs):
    """ Constructs a retinanet model using a resnet backbone.

    Args
        num_classes: Number of classes to predict.
        backbone: Which backbone to use (one of ('EfficientNetB0', 'EfficientNetB1', ... , 'EfficientNetB7')).
        inputs: The inputs to the network (defaults to a Tensor of shape (None, None, 3)).
        modifier: A function handler which can modify the backbone before using it in retinanet (this can be used to freeze backbone layers for example).

    Returns
        RetinaNet model with a EfficientNet backbone.
    """
    # choose default input
    if inputs is None:
        if keras.backend.image_data_format() == 'channels_first':
            inputs = keras.layers.Input(shape=(3, None, None))
        else:
            # inputs = keras.layers.Input(shape=(224, 224, 3))
            inputs = keras.layers.Input(shape=(None, None, 3))

    # get last conv layer from the end of each block [28x28, 14x14, 7x7]
    if backbone == 'EfficientNetB0':
        model = effnet.EfficientNetB0(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB1':
        model = effnet.EfficientNetB1(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB2':
        model = effnet.EfficientNetB2(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB3':
        model = effnet.EfficientNetB3(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB4':
        model = effnet.EfficientNetB4(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB5':
        model = effnet.EfficientNetB5(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB6':
        model = effnet.EfficientNetB6(input_tensor=inputs, include_top=False, weights=None)
    elif backbone == 'EfficientNetB7':
        model = effnet.EfficientNetB7(input_tensor=inputs, include_top=False, weights=None)
    else:
        raise ValueError('Backbone (\'{}\') is invalid.'.format(backbone))

    layer_outputs = ['block4a_expand_activation', 'block6a_expand_activation', 'top_activation']

    layer_outputs = [
        model.get_layer(name=layer_outputs[0]).output,  # 28x28
        model.get_layer(name=layer_outputs[1]).output,  # 14x14
        model.get_layer(name=layer_outputs[2]).output,  # 7x7
    ]
    # create the densenet backbone
    model = keras.models.Model(inputs=inputs, outputs=layer_outputs, name=model.name)

    # invoke modifier if given
    if modifier:
        model = modifier(model)

    # create the full model
    return retinanet.retinanet(inputs=inputs, num_classes=num_classes, backbone_layers=model.outputs, **kwargs)


def EfficientNetB0_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB0', inputs=inputs, **kwargs)


def EfficientNetB1_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB1', inputs=inputs, **kwargs)


def EfficientNetB2_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB2', inputs=inputs, **kwargs)


def EfficientNetB3_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB3', inputs=inputs, **kwargs)


def EfficientNetB4_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB4', inputs=inputs, **kwargs)


def EfficientNetB5_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB5', inputs=inputs, **kwargs)


def EfficientNetB6_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB6', inputs=inputs, **kwargs)


def EfficientNetB7_retinanet(num_classes, inputs=None, **kwargs):
    return effnet_retinanet(num_classes=num_classes, backbone='EfficientNetB7', inputs=inputs, **kwargs)
