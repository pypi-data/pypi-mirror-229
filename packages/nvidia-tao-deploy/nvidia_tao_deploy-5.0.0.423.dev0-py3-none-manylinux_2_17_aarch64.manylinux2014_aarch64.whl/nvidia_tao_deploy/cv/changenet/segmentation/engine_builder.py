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

"""ChangeNet TensorRT engine builder."""

import logging
import os
import sys
import onnx

import tensorrt as trt

from nvidia_tao_deploy.engine.builder import EngineBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChangeNetEngineBuilder(EngineBuilder):
    """Parses an ONNX graph and builds a TensorRT engine from it."""

    def __init__(
        self,
        data_format="channels_first",
        img_std=[0.229, 0.224, 0.225],
        **kwargs
    ):
        """Init.

        Args:
            data_format (str): data_format.
        """
        super().__init__(**kwargs)
        self._data_format = data_format
        self._img_std = img_std

    def set_input_output_node_names(self):
        """Set input output node names."""
        self._output_node_names = ["output0", "output1", 'output2', 'output3', 'output_final']
        self._input_node_names = ['input0', 'input1']

    def get_onnx_input_dims(self, model_path):
        """Get input dimension of ONNX model."""
        onnx_model = onnx.load(model_path)
        onnx_inputs = onnx_model.graph.input
        logger.info('List inputs:')
        input_dims = {}
        for i, inputs in enumerate(onnx_inputs):
            logger.info('Input %s -> %s.', i, inputs.name)
            logger.info('%s.', [i.dim_value for i in inputs.type.tensor_type.shape.dim][1:])
            logger.info('%s.', [i.dim_value for i in inputs.type.tensor_type.shape.dim][0])
            input_dims[inputs.name] = [i.dim_value for i in inputs.type.tensor_type.shape.dim][:]
        return input_dims

    def create_network(self, model_path, file_format="onnx"):
        """Parse the UFF/ONNX graph and create the corresponding TensorRT network definition.

        Args:
            model_path: The path to the UFF/ONNX graph to load.
            file_format: The file format of the decrypted etlt file (default: onnx).
        """
        if file_format == "onnx":
            logger.info("Parsing ONNX model")
            self._input_dims = self.get_onnx_input_dims(model_path)

            batch_sizes = {v[0] for v in self._input_dims.values()}
            assert len(batch_sizes), (
                "All tensors should have the same batch size."
            )
            self.batch_size = list(batch_sizes)[0]
            for k, v in self._input_dims.items():
                self._input_dims[k] = v[1:]

            network_flags = 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
            network_flags = network_flags | (1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_PRECISION))

            self.network = self.builder.create_network(network_flags)
            self.parser = trt.OnnxParser(self.network, self.trt_logger)
            model_path = os.path.realpath(model_path)
            with open(model_path, "rb") as f:
                if not self.parser.parse(f.read()):
                    logger.error("Failed to load ONNX file: %s", model_path)
                    for error in range(self.parser.num_errors):
                        logger.error(self.parser.get_error(error))
                    sys.exit(1)

            inputs = [self.network.get_input(i) for i in range(self.network.num_inputs)]
            outputs = [self.network.get_output(i) for i in range(self.network.num_outputs)]
            logger.info("Network Description")
            for input in inputs: # noqa pylint: disable=W0622
                logger.info("Input '%s' with shape %s and dtype %s", input.name, input.shape, input.dtype)
            for output in outputs:
                logger.info("Output '%s' with shape %s and dtype %s", output.name, output.shape, output.dtype)

            if self.batch_size <= 0:  # dynamic batch size
                logger.info("dynamic batch size handling")
                opt_profile = self.builder.create_optimization_profile()
                for i in range(self.network.num_inputs):
                    model_input = self.network.get_input(i)
                    input_shape = model_input.shape
                    input_name = model_input.name
                    real_shape_min = (
                        self.min_batch_size, input_shape[1],
                        input_shape[2], input_shape[3]
                    )
                    real_shape_opt = (
                        self.opt_batch_size, input_shape[1],
                        input_shape[2], input_shape[3]
                    )
                    real_shape_max = (
                        self.max_batch_size, input_shape[1],
                        input_shape[2], input_shape[3]
                    )
                    opt_profile.set_shape(
                        input=input_name,
                        min=real_shape_min,
                        opt=real_shape_opt,
                        max=real_shape_max
                    )
                self.config.add_optimization_profile(opt_profile)
                self.config.set_calibration_profile(opt_profile)

        else:
            logger.info("Parsing UFF model")
            raise NotImplementedError("UFF for ChangeNet is not supported")

    def create_engine(self, engine_path, precision,
                      calib_input=None, calib_cache=None, calib_num_images=5000,
                      calib_batch_size=8, calib_data_file=None):
        """Build the TensorRT engine and serialize it to disk.

        Args:
            engine_path: The path where to serialize the engine to.
            precision: The datatype to use for the engine, either 'fp32', 'fp16' or 'int8'.
            calib_input: The path to a directory holding the calibration images.
            calib_cache: The path where to write the calibration cache to,
                         or if it already exists, load it from.
            calib_num_images: The maximum number of images to use for calibration.
            calib_batch_size: The batch size to use for the calibration process.
        """
        engine_path = os.path.realpath(engine_path)
        engine_dir = os.path.dirname(engine_path)
        os.makedirs(engine_dir, exist_ok=True)
        logger.debug("Building %s Engine in %s", precision, engine_path)

        if self.batch_size is None:
            self.batch_size = calib_batch_size
            self.builder.max_batch_size = self.batch_size

        if precision == "fp16":
            if not self.builder.platform_has_fast_fp16:
                logger.warning("FP16 is not supported natively on this platform/device")
            else:
                self.config.set_flag(trt.BuilderFlag.FP16)
        elif precision == "int8":
            raise NotImplementedError("INT8 is not supported for ChangeNet!")

        self._logger_info_IBuilderConfig()
        with self.builder.build_engine(self.network, self.config) as engine, \
                open(engine_path, "wb") as f:
            logger.debug("Serializing engine to file: %s", engine_path)
            f.write(engine.serialize())
