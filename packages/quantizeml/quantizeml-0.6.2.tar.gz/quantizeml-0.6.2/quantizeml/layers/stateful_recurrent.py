#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************

__all__ = ["StatefulRecurrent", "reset_states"]

import keras
import tensorflow as tf


@tf.keras.utils.register_keras_serializable()
class StatefulRecurrent(keras.layers.Layer):
    """ A recurrent layer with an internal state.

    Args:
        num_coeffs (int): number of embedding coefficients
        repeat (int, optional): number of times to repeat the embedding coefficients. The total
            hidden dimension (the internal state units) is given simply by num_coeffs x repeat.
            Defaults to 2.
        subsample_ratio (float, optional): subsampling ratio that defines rate at which outputs are
            produced (zero otherwise). Defaults to 1.
    """

    def __init__(self, *args, num_coeffs, repeat=2, subsample_ratio=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_coeffs = num_coeffs
        self.repeat = repeat
        self.subsample_ratio = subsample_ratio
        self.reset_states()

    def build(self, input_shape):
        super().build(input_shape)
        # 'A' weight is a complex64 tensor stored as two float32 tensor to ease quantization
        self.A_real = self.add_weight(name='A_real', shape=(self.repeat * self.num_coeffs,))
        self.A_imag = self.add_weight(name='A_imag', shape=(self.repeat * self.num_coeffs,))

    def call(self, inputs):
        """ This call method only takes in a single input step.

        For every input step, the internal state is updated using the inputs which should be the
        updated state from the previous layer.
        """
        if self.internal_state_real is None:
            self.internal_state_real = tf.zeros_like(inputs)
            self.internal_state_imag = tf.zeros_like(inputs)

        if self.subsample_ratio:
            self.counter += 1
            # Path for skipping computations
            if self.counter % self.subsample_ratio != 0:
                return tf.zeros_like(inputs)

        # Update internal state: compute real and imaginary part separately
        updated_real = self.internal_state_real * self.A_real - \
            self.internal_state_imag * self.A_imag + inputs
        self.internal_state_imag = self.A_imag * self.internal_state_real + \
            self.A_real * self.internal_state_imag
        # Update real part in a second time so that it does not impact imaginary part computation
        self.internal_state_real = updated_real

        return self.internal_state_real

    def reset_states(self):
        """ Reset internal state to zero.
        """
        # 'internal_state' is a complex64 tensor stored as two float32 tensor to ease quantization
        self.internal_state_real, self.internal_state_imag = None, None
        self.counter = 0

    def get_config(self):
        config = super().get_config()
        config.update({
            'num_coeffs': self.num_coeffs,
            'repeat': self.repeat,
            'subsample_ratio': self.subsample_ratio
        })
        return config


def reset_states(model):
    """ Resets all StatefulRecurrent layers internal states in the model.

    Args:
        model (keras.Model): the model to reset
    """
    for layer in model.layers:
        if isinstance(layer, StatefulRecurrent):
            layer.reset_states()
