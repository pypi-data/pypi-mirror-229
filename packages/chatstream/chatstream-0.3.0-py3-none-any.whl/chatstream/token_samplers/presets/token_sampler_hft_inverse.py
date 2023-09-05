"""

Copyright (c) 2023 Qualiteg Inc. all rights reserved.

This program is dual-licensed under the terms of the:
1) GNU Affero General Public License, version 3, or any later version.
2) A commercial license agreement provided by Qualiteg Inc.

If you choose to use or redistribute this program under the terms of AGPLv3:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

If you wish to use or redistribute this program under a commercial license:
Please contact Qualiteg Inc.(https://qualiteg.com/contact) directly to obtain the terms and pricing.

"""
from chatstream.token_samplers.token_sampler_base import TokenSamplerBase
from chatstream.token_samplers.token_sampler_builder import TokenSamplerBuilder


class TokenSamplerHftInverse(TokenSamplerBase):
    """
    HuggingFace Transformer(HFT) Sampler like TokenSampler

    HuggingFaceのTransformerで採用されているオーソドックスなサンプラーの適用順序のうち
    top_pとtop_kの順序を入れ替えたもの

    """

    def __init__(self):
        sampler = TokenSamplerBuilder()
        # フィルター適用順序
        # check => rep_penalty => temperature => top_k_sampling => top_p_sampling => softmax
        sampler.append("check")  # 1: logits適正化プロセッサ
        sampler.append("rep_penalty")  # 2: 繰り返しペナルティプロセッサ
        sampler.append("temperature")  # 3: 温度スケーリングプロセッサ
        sampler.append("top_p_sampling")  # 4: top_p サンプラー
        sampler.append("top_k_sampling")  # 5: top_k サンプラー
        sampler.append("softmax")  # 6: softmax サンプラー

        self.sampler = sampler

    def get_sampler(self):
        return self.sampler
