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


def setup_gpu(gpu_id):
    try:
        visible_gpu_indices = [int(id) for id in gpu_id.split(',')]
        available_gpus = tf.config.list_physical_devices('GPU')
        visible_gpus = [gpu for idx, gpu in enumerate(available_gpus) if idx in visible_gpu_indices]

        if visible_gpus:
            try:
                # Currently, memory growth needs to be the same across GPUs.
                for gpu in available_gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)

                # Use only the selcted gpu.
                tf.config.set_visible_devices(visible_gpus, 'GPU')
            except RuntimeError as e:
                # Visible devices must be set before GPUs have been initialized.
                print(e)

            logical_gpus = tf.config.list_logical_devices('GPU')
            print(len(available_gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        else:
            tf.config.set_visible_devices([], 'GPU')
    except ValueError:
        tf.config.set_visible_devices([], 'GPU')
