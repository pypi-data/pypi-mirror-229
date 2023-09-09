# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility class for performing TensorRT image inference."""

import logging
import numpy as np

import tensorrt as trt

from nvidia_tao_deploy.inferencer.trt_inferencer import TRTInferencer
from nvidia_tao_deploy.inferencer.utils import allocate_buffers, do_inference
from nvidia_tao_deploy.cv.changenet.segmentation.utils import ConfuseMatrixMeter


logger = logging.getLogger(__name__)


def trt_output_process_fn(y_encoded, model_output_width, model_output_height, n_class=2):
    """Function to process TRT model output."""
    predictions_batch = []
    for idx in range(y_encoded.shape[0]):
        pred = np.reshape(y_encoded[idx], (n_class, model_output_height, model_output_width))
        predictions_batch.append(pred)

    return np.array(predictions_batch)


class ChangeNetInferencer(TRTInferencer):
    """Manages TensorRT objects for model inference."""

    def __init__(self, engine_path, input_shape=None, batch_size=None, data_format="channel_first", n_class=2, mode='test'):
        """Initializes TensorRT objects needed for model inference.

        Args:
            engine_path (str): path where TensorRT engine should be stored
            input_shape (tuple): (batch, channel, height, width) for dynamic shape engine
            batch_size (int): batch size for dynamic shape engine
            data_format (str): either channel_first or channel_last
        """
        # Load TRT engine
        logger.info("Loading engine from {}".format(engine_path))
        super().__init__(engine_path) # noqa pylint: disable=W0612
        self.execute_v2 = True
        self.n_class = n_class
        self.mode = mode

        # Allocate memory for multiple usage [e.g. multiple batch inference]
        self._input_shape = []
        for binding in range(self.engine.num_bindings):
            if self.engine.binding_is_input(binding):
                self._input_shape.append(self.engine.get_binding_shape(binding)[-3:])
                self.max_batch_size = self.engine.get_binding_shape(binding)[0]
        for shape in self._input_shape:
            assert len(shape) == 3, "Engine doesn't have valid input dimensions"

        if data_format == "channel_first":
            self.height = self._input_shape[0][1]
            self.width = self._input_shape[0][2]
        else:
            self.height = self._input_shape[0][0]
            self.width = self._input_shape[0][1]

        # set binding_shape for dynamic input
        # When using dynamic batching, need to set shape of each of binding_id to be
        # bs, 3, height, width. By default bs = -1, so need to set it to the input bs
        for binding in range(self.engine.num_bindings):
            if self.engine.binding_is_input(binding):
                binding_id = self.engine.get_binding_index(str(binding))
                if (input_shape is not None) or (batch_size is not None):
                    self.context = self.engine.create_execution_context()
                    if input_shape is not None:
                        for idx, _input_shape in enumerate(input_shape):
                            self.context.set_binding_shape(binding_id, _input_shape[idx])
                            self.max_batch_size = _input_shape[idx][0]
                    else:
                        for idx, _input_shape in enumerate(self._input_shape):
                            self.context.set_binding_shape(idx, [batch_size] + list(_input_shape))
                            self.max_batch_size = batch_size
            self.execute_v2 = True

        # This allocates memory for network inputs/outputs on both CPU and GPU
        self.inputs, self.outputs, self.bindings, self.stream = allocate_buffers(self.engine,
                                                                                 self.context)
        if self.context is None:
            self.context = self.engine.create_execution_context()

        input_volumes = [trt.volume(shape) for shape in self._input_shape]
        self.numpy_array = [
            np.zeros((self.max_batch_size, volume)) for volume in input_volumes
        ]
        if mode == 'test':
            self.running_metric = ConfuseMatrixMeter(n_class=n_class)

    def infer(self, imgs, target=None):  # noqa pylint: disable=W0237
        """Infers model on batch of same sized images resized to fit the model.

        Args:
            image_paths (str): paths to images, that will be packed into batch
                and fed into model
        """
        # Verify if the supplied batch size is not too big
        max_batch_size = self.max_batch_size
        for idx, input_image in enumerate(imgs, start=0):
            actual_batch_size = len(input_image)
            if actual_batch_size > max_batch_size:
                raise ValueError(
                    f"image_paths list bigger ({actual_batch_size}) than "
                    f"engine max batch size ({max_batch_size})"
                )

            self.numpy_array[idx][:actual_batch_size] = input_image.reshape(actual_batch_size, -1)
            # ...copy them into appropriate place into memory...
            # (self.inputs was returned earlier by allocate_buffers())
            np.copyto(self.inputs[idx].host, self.numpy_array[idx].ravel())

        # ...fetch model outputs...
        results = do_inference(
            self.context, bindings=self.bindings, inputs=self.inputs,
            outputs=self.outputs, stream=self.stream,
            batch_size=max_batch_size,
            execute_v2=self.execute_v2)

        # ...and return results up to the actual batch size.
        y_pred = [i.reshape(max_batch_size, -1)[:actual_batch_size] for i in results]
        # Process TRT outputs to proper format using last FM output segmentation map
        y_pred = trt_output_process_fn(y_pred[-1], self.width, self.height, self.n_class)
        if self.mode == 'test':
            self._update_metric(y_pred, target)
        return y_pred

    def __del__(self):
        """Clear things up on object deletion."""
        # Clear session and buffer
        if self.trt_runtime:
            del self.trt_runtime

        if self.context:
            del self.context

        if self.engine:
            del self.engine

        if self.stream:
            del self.stream

        # Loop through inputs and free inputs.
        for inp in self.inputs:
            inp.device.free()

        # Loop through outputs and free them.
        for out in self.outputs:
            out.device.free()

    def _update_metric(self, pred, target):
        """Calculates running metrics for evaluation"""
        pred = np.argmax(pred, axis=1, keepdims=True)
        current_score = self.running_metric.update_cm(pr=pred, gt=target)

        return current_score
