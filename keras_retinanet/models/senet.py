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
from classification_models.keras import Classifiers


class SeBackbone(Backbone):
    """ Describes backbone information and provides utility functions.
    """

    def __init__(self, backbone):
        super(SeBackbone, self).__init__(backbone)
        _, self.preprocess_image_func = Classifiers.get(self.backbone)

    def retinanet(self, *args, **kwargs):
        """ Returns a retinanet model using the correct backbone.
        """
        return senet_retinanet(*args, backbone=self.backbone, **kwargs)

    def download_imagenet(self):
        """ Downloads ImageNet weights and returns path to weights file.
        """
        from classification_models.weights import WEIGHTS_COLLECTION

        weights_path = None
        for el in WEIGHTS_COLLECTION:
            if el['model'] == self.backbone and not el['include_top']:
                weights_path = get_file(el['name'], el['url'], cache_subdir='models', file_hash=el['md5'])

        if weights_path is None:
            raise ValueError('Unable to find imagenet weights for backbone {}!'.format(self.backbone))

        return weights_path

    def validate(self):
        """ Checks whether the backbone string is correct.
        """
        allowed_backbones = ['senet154']
        backbone = self.backbone.split('_')[0]

        if backbone not in allowed_backbones:
            raise ValueError('Backbone (\'{}\') not in allowed backbones ({}).'.format(backbone, allowed_backbones))

    def preprocess_image(self, inputs):
        """ Takes as input an image and prepares it for being passed through the network.
        """
        return self.preprocess_image_func(inputs)


def senet_retinanet(num_classes, backbone='senet154', inputs=None, modifier=None, **kwargs):
    """ Constructs a retinanet model using a resnet backbone.
    Args
        num_classes: Number of classes to predict.
        backbone: Which backbone to use (one of ('senet154')).
        inputs: The inputs to the network (defaults to a Tensor of shape (None, None, 3)).
        modifier: A function handler which can modify the backbone before using it in retinanet (this can be used to freeze backbone layers for example).
    Returns
        RetinaNet model with a SeNet backbone.
    """
    # choose default input
    if inputs is None:
        if keras.backend.image_data_format() == 'channels_first':
            inputs = keras.layers.Input(shape=(3, None, None))
        else:
            inputs = keras.layers.Input(shape=(None, None, 3))

    classifier, _ = Classifiers.get(backbone)
    model = classifier(input_tensor=inputs, include_top=False, weights=None)

    # get last conv layer from the end of each block [28x28, 14x14, 7x7]
    if backbone == 'senet154':
        layer_outputs = ['activation_59', 'activation_239', 'activation_253']
    else:
        raise ValueError('Backbone (\'{}\') is invalid.'.format(backbone))

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

def senet154_retinanet(num_classes, inputs=None, **kwargs):
    return senet_retinanet(num_classes=num_classes, backbone='senet154', inputs=inputs, **kwargs)