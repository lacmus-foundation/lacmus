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

from . import Backbone
from . import retinanet

from ..utils.image import preprocess_image

import keras
from keras.applications import mobilenet
from keras.utils import get_file

from .mobilenetv3.mobilenet_v3_large import MobileNetV3_Large
from .mobilenetv3.mobilenet_v3_small import MobileNetV3_Small


class MobileNetV3Backbone(Backbone):
    """ Describes backbone information and provides utility functions.
    """

    allowed_backbones = ['mobilenet_v3_small', 'mobilenet_v3_large']

    def retinanet(self, *args, **kwargs):
        """ Returns a retinanet model using the correct backbone.
        """
        return mobilenetv3_retinanet(*args, backbone_name=self.backbone, **kwargs)


    def validate(self):
        """ Checks whether the backbone string is correct.
        """
        name_parts = self.backbone.split('_')

        if '_'.join(name_parts[:3]) not in MobileNetV3Backbone.allowed_backbones:
            raise ValueError('Backbone (\'{}\') not in allowed backbones ({}).'.format(backbone, MobileNetV3Backbone.allowed_backbones))

    def preprocess_image(self, inputs):
        """ Takes as input an image and prepares it for being passed through the network.
        """
        return preprocess_image(inputs, mode='tf')


def mobilenetv3_retinanet(num_classes, backbone_name='mobilenet_v3_small', inputs=None, modifier=None, **kwargs):
    """ Constructs a retinanet model using a mobilenet backbone.

    Args
        num_classes: Number of classes to predict.
        backbone: Which backbone to use (mobilenet_v3_small or mobilenet_v3_large).
        inputs: The inputs to the network (defaults to a Tensor of shape (None, None, 3)).
        modifier: A function handler which can modify the backbone before using it in retinanet (this can be used to freeze backbone layers for example).

    Returns
        RetinaNet model with a MobileNet backbone.
    """
    name_parts = backbone_name.split('_')
    if len(name_parts) > 3:
    	alpha = float(name_parts[3])
    else:
        alpha = 1.0 

    # choose default input
    if inputs is None:
        if keras.backend.image_data_format() == 'channels_first':
            shape=(3, None, None)
        else:
            shape=(None, None, 3)
    else:
        shape = inputs.shape

    if 'mobilenet_v3_small' in backbone_name: 
    	backbone = MobileNetV3_Small(shape=shape, n_class=1, alpha=alpha, include_top=False).build()
    	layer_outputs = [
            backbone.layers[30].output, # activation_7, bneck 3 before pw, 28x28x88
	        backbone.layers[98].output, # multiply_5, bneck 8 before pwl, 14x14x144 
	        backbone.layers[145].output # activation_24, just before global pooling, 7x7x576
        ]
    elif 'mobilenet_v3_large' in backbone_name:
        backbone = MobileNetV3_Large(shape=shape, n_class=1, alpha=alpha, include_top=False).build() 
        layer_outputs = [
            backbone.layers[67].output, # multiply_3, bneck 6 before pwl, 28x28x120
	        backbone.layers[129].output, # multiply_5, bneck 12 before pwl, 14x14x672
	        backbone.layers[176].output # activation_32, just before global pooling, 7x7x960
        ]

    inputs = backbone.inputs
    # create the full model
    backbone = keras.models.Model(inputs=inputs, outputs=layer_outputs, name=backbone_name)

    # invoke modifier if given
    if modifier:
        backbone = modifier(backbone)

    return retinanet.retinanet(inputs=inputs, num_classes=num_classes, backbone_layers=backbone.outputs, **kwargs)
