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

import tensorflow as tf

from .tf_version import tf_version_ok


def setup_gpu(gpu_id):
    if tf_version_ok((2, 0, 0)):
        if gpu_id == 'cpu' or gpu_id == -1:
            tf.config.experimental.set_visible_devices([], 'GPU')
            return

        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            # Restrict TensorFlow to only use the first GPU.
            try:
                # Currently, memory growth needs to be the same across GPUs.
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)

                # Use only the selcted gpu.
                tf.config.experimental.set_visible_devices(gpus[int(gpu_id)], 'GPU')
            except RuntimeError as e:
                # Visible devices must be set before GPUs have been initialized.
                print(e)

            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    else:
        import os
        if gpu_id == 'cpu' or gpu_id == -1:
            os.environ['CUDA_VISIBLE_DEVICES'] = ""
            return

        os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        tf.keras.backend.set_session(tf.Session(config=config))
