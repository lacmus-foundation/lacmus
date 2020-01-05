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

from __future__ import print_function

import tensorflow as tf
import sys

MINIMUM_TF_VERSION = 1, 14, 0


def tf_version():
    """ Get the Tensorflow version.
        Returns
            tuple of (major, minor, patch).
    """
    return tuple(map(int, tf.version.VERSION.split('-')[0].split('.')))


def tf_version_ok(minimum_tf_version=MINIMUM_TF_VERSION):
    """ Check if the current Tensorflow version is higher than the minimum version.
    """
    return tf_version() >= minimum_tf_version


def assert_tf_version(minimum_tf_version=MINIMUM_TF_VERSION):
    """ Assert that the Tensorflow version is up to date.
    """
    detected = tf.version.VERSION
    required = '.'.join(map(str, minimum_tf_version))
    assert(tf_version() >= minimum_tf_version), 'You are using tensorflow version {}. The minimum required version is {}.'.format(detected, required)


def check_tf_version():
    """ Check that the Tensorflow version is up to date. If it isn't, print an error message and exit the script.
    """
    try:
        assert_tf_version()
    except AssertionError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
