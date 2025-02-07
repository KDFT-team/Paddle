# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
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

import unittest

import numpy as np
from inference_pass_test import InferencePassTest

import paddle
from paddle import fluid
from paddle.fluid import core
from paddle.fluid.core import AnalysisConfig, PassVersionChecker
from paddle.static import nn


class TRTReduceSumTest(InferencePassTest):
    def setUp(self):
        with fluid.program_guard(self.main_program, self.startup_program):
            data = paddle.static.data(
                name="data", shape=[-1, 3, 10, 192], dtype="float32"
            )
            reduce_sum = paddle.sum(data, axis=[2, -1], keepdim=True)
            out = nn.batch_norm(reduce_sum, is_test=True)

        self.feeds = {
            "data": np.random.random([3, 3, 10, 192]).astype("float32"),
        }
        self.enable_trt = True
        self.trt_parameters = TRTReduceSumTest.TensorRTParam(
            1 << 30, 32, 1, AnalysisConfig.Precision.Float32, False, False
        )
        self.fetch_list = [out]
        self.dynamic_shape_params = TRTReduceSumTest.DynamicShapeParam(
            {'data': [1, 3, 8, 8]},
            {'data': [3, 3, 10, 192]},
            {'data': [3, 3, 10, 192]},
            False,
        )

    def test_check_output(self):
        if core.is_compiled_with_cuda():
            use_gpu = True
            self.check_output_with_option(use_gpu, flatten=True)
            self.assertTrue(
                PassVersionChecker.IsCompatible('tensorrt_subgraph_pass')
            )


class TRTReduceSumAllTest(InferencePassTest):
    def setUp(self):
        with fluid.program_guard(self.main_program, self.startup_program):
            data = paddle.static.data(
                name="data", shape=[-1, 3, 10, 192], dtype="float32"
            )
            reduce_sum = paddle.sum(data, keepdim=True)
            out = nn.batch_norm(reduce_sum, is_test=True)

        self.feeds = {
            "data": np.random.random([3, 3, 10, 192]).astype("float32"),
        }
        self.enable_trt = True
        self.trt_parameters = TRTReduceSumAllTest.TensorRTParam(
            1 << 30, 32, 1, AnalysisConfig.Precision.Float32, False, False
        )
        self.fetch_list = [out]
        self.dynamic_shape_params = TRTReduceSumAllTest.DynamicShapeParam(
            {'data': [1, 3, 8, 8]},
            {'data': [3, 3, 10, 192]},
            {'data': [3, 3, 10, 192]},
            False,
        )

    def test_check_output(self):
        if core.is_compiled_with_cuda():
            use_gpu = True
            self.check_output_with_option(use_gpu, flatten=True)
            self.assertTrue(
                PassVersionChecker.IsCompatible('tensorrt_subgraph_pass')
            )


if __name__ == "__main__":
    unittest.main()
