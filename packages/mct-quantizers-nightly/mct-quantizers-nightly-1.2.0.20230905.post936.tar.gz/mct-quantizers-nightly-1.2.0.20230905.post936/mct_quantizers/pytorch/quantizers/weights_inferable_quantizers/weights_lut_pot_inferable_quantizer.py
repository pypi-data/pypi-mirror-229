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
    from mct_quantizers.pytorch.quantizers.weights_inferable_quantizers.weights_lut_symmetric_inferable_quantizer \
        import \
        WeightsLUTSymmetricInferableQuantizer


    @mark_quantizer(quantization_target=QuantizationTarget.Weights,
                    quantization_method=[QuantizationMethod.LUT_POT_QUANTIZER],
                    identifier=QuantizerID.INFERABLE)
    class WeightsLUTPOTInferableQuantizer(WeightsLUTSymmetricInferableQuantizer):
        """
        Class for quantizing weights using lut power-of-two quantizer
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
            # target of Weights quantization
            super(WeightsLUTPOTInferableQuantizer, self).__init__(num_bits=num_bits,
                                                                  threshold=threshold,
                                                                  lut_values=lut_values,
                                                                  per_channel=per_channel,
                                                                  channel_axis=channel_axis,
                                                                  lut_values_bitwidth=lut_values_bitwidth,
                                                                  eps=eps)

            is_threshold_pot = np.all(np.round(np.log2(threshold.flatten())) == np.log2(threshold.flatten()))
            assert is_threshold_pot, f'Expected threshold to be power of 2 but is {threshold}'


else:
    class WeightsLUTPOTInferableQuantizer:  # pragma: no cover
        def __init__(self, *args, **kwargs):
            raise Exception('Installing torch is mandatory '
                            'when using WeightsLUTPOTInferableQuantizer. '
                            'Could not find torch package.')
