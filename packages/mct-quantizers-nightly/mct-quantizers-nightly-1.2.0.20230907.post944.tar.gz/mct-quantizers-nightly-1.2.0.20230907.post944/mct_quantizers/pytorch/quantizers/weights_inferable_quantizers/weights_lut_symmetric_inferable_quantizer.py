# Copyright 2023 Sony Semiconductor Israel, Inc. All rights reserved.
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
# ==============================================================================

import numpy as np

from mct_quantizers.common.base_inferable_quantizer import mark_quantizer, QuantizationTarget, QuantizerID
from mct_quantizers.common.constants import FOUND_TORCH, LUT_VALUES_BITWIDTH, EPS
from mct_quantizers.common.quant_info import QuantizationMethod

if FOUND_TORCH:
    import torch
    from mct_quantizers.pytorch.quantizer_utils import to_torch_tensor, get_working_device, lut_quantizer
    from mct_quantizers.pytorch.quantizers.base_lut_symmetric_inferable_quantizer import \
        BaseLUTSymmetricInferableQuantizer


    @mark_quantizer(quantization_target=QuantizationTarget.Weights,
                    quantization_method=[QuantizationMethod.LUT_SYM_QUANTIZER],
                    identifier=QuantizerID.INFERABLE)
    class WeightsLUTSymmetricInferableQuantizer(BaseLUTSymmetricInferableQuantizer):
        """
        Class for quantizing weights using a lut symmetric quantizer
        """

        def __init__(self,
                     num_bits: int,
                     lut_values: np.ndarray,
                     threshold: np.ndarray,
                     per_channel: bool,
                     channel_axis: int = None,
                     lut_values_bitwidth: int = LUT_VALUES_BITWIDTH,
                     eps: float = EPS):
            """
            Initialize the quantizer with the specified parameters.

            Args:
                num_bits: number of bits to use for quantization
                lut_values: the values in the look-up table to assign the weights to
                threshold: threshold for quantizing weights
                per_channel: whether to use per-channel quantization
                channel_axis: Axis of input to apply per-channel quantization on
                lut_values_bitwidth: Number of bits that determines the quantization range
                eps: Small value for numerical stability in division
            """

            super(WeightsLUTSymmetricInferableQuantizer, self).__init__(threshold=threshold,
                                                                        num_bits=num_bits,
                                                                        lut_values=lut_values,
                                                                        signed=True,
                                                                        lut_values_bitwidth=lut_values_bitwidth,
                                                                        eps=eps)

            if per_channel:
                assert channel_axis is not None, f'Channel axis is missing in per channel quantization'
                assert len(
                    threshold) >= 1, f'In per-channel quantization threshold should be of length >= 1 but is ' \
                                     f'{len(threshold)}'
            else:
                assert len(
                    threshold) == 1, f'In per-tensor quantization threshold should be of length 1 but is ' \
                                     f'{len(threshold)}'

            self.per_channel = per_channel
            self.channel_axis = channel_axis

            self.threshold = to_torch_tensor(self.threshold).to(get_working_device())
            self.lut_values = to_torch_tensor(self.lut_values).to(get_working_device())

        def __call__(self, inputs: torch.Tensor) -> torch.Tensor:
            """
            Quantize the given inputs using the quantizer parameters.

            Args:
                inputs: input tensor to quantize

            Returns:
                quantized tensor.
            """
            inputs.requires_grad = False
            return lut_quantizer(inputs, lut_values=self.lut_values, signed=True,
                                 threshold=self.threshold, lut_values_bitwidth=self.lut_values_bitwidth, eps=self.eps)


else:
    class WeightsLUTSymmetricInferableQuantizer:  # pragma: no cover
        def __init__(self, *args, **kwargs):
            raise Exception('Installing torch is mandatory '
                            'when using WeightsLUTSymmetricInferableQuantizer. '
                            'Could not find torch package.')
