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

"""Standalone TensorRT inference."""


import os
import logging
import numpy as np
from tqdm import tqdm

from nvidia_tao_deploy.cv.common.decorators import monitor_status
from nvidia_tao_deploy.cv.common.hydra.hydra_runner import hydra_runner
from nvidia_tao_deploy.cv.changenet.hydra_config.default_config import ExperimentConfig
from nvidia_tao_deploy.cv.changenet.segmentation.inferencer import ChangeNetInferencer as ChangeNetSegmentInferencer
from nvidia_tao_deploy.cv.changenet.segmentation.dataloader import ChangeNetDataLoader as ChangeNetSegmentDataLoader
from nvidia_tao_deploy.cv.changenet.segmentation.utils import get_color_mapping, visualize_infer_output

logging.basicConfig(format='%(asctime)s [TAO Toolkit] [%(levelname)s] %(name)s %(lineno)d: %(message)s',
                    level="INFO")
logger = logging.getLogger(__name__)
spec_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@hydra_runner(
    config_path=os.path.join(spec_root, "specs"),
    config_name="infer", schema=ExperimentConfig
)
@monitor_status(name='changenet', mode='inference')
def main(cfg: ExperimentConfig) -> None:
    """changenet TRT Inference."""
    if not os.path.exists(cfg.inference.trt_engine):
        raise FileNotFoundError(f"Provided inference.trt_engine at {cfg.inference.trt_engine} does not exist!")

    logger.info("Running inference")
    engine_file = cfg.inference.trt_engine
    batch_size = cfg.inference.batch_size
    dataset_config = cfg.dataset.segment

    # Create results directories
    if cfg.inference.results_dir is not None:
        results_dir = cfg.inference.results_dir
    else:
        results_dir = os.path.join(cfg.results_dir, "trt_inference")
    os.makedirs(results_dir, exist_ok=True)

    logger.info("Instantiate the ChangeNet inferencer.")
    changenet_inferencer = ChangeNetSegmentInferencer(
        engine_path=engine_file,
        batch_size=batch_size,
        n_class=dataset_config.num_classes,
        mode='predict'
    )

    logger.info("Instantiating the ChangeNet dataloader.")
    infer_dataloader = ChangeNetSegmentDataLoader(
        dataset_config=dataset_config,
        dtype=changenet_inferencer.inputs[0].host.dtype,
        split=dataset_config.predict_split
    )

    total_num_samples = len(infer_dataloader)
    logger.info("Number of sample batches: {}".format(total_num_samples))
    logger.info("Running inference")

    # Color map for segmentation output visualisation for multi-class output
    color_map = get_color_mapping(dataset_name=dataset_config.data_name,
                                  color_mapping_custom=dataset_config.color_map,
                                  num_classes=dataset_config.num_classes)

    # Inference
    for idx, (img_1, img_2) in tqdm(enumerate(infer_dataloader), total=total_num_samples):
        input_batches = [
            img_1,
            img_2
        ]
        image_paths = infer_dataloader.img_name_list[np.arange(batch_size) + batch_size * idx]
        results = changenet_inferencer.infer(input_batches)

        # Save output visualisation
        for img1, img2, result, img_path in zip(img_1, img_2, results, image_paths):
            visualize_infer_output(img_path, result, img1, img2, dataset_config.num_classes,
                                   color_map, results_dir, mode='predict')

    logging.info("Finished inference.")


if __name__ == '__main__':
    main()
