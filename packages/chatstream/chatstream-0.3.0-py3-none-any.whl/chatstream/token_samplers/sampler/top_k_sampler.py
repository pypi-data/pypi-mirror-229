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

import torch

from chatstream.token_samplers.logits_processor import AbstractLogitsProcessor
from chatstream.token_samplers.sampler.top_n_sampler_def import BIGGER_NUMBER_TO_FILTER_FP32, BIGGER_NUMBER_TO_FILTER_FP16


class TopKSampler(AbstractLogitsProcessor):
    """
    top_k サンプリングを行う

    top_kサンプリングは与えられたlogitsから最も大きい確率のtop_kトークンのみを考慮するため、そのほかのlogitの値を限りなく小さくする

    この処理では、softmax前のlogitsのうち、top_k以外のものは無効化（具体的には値を-float("Inf")に設定）する
    そのため、softmax関数を適用した際に、この効果により無効化されたlogitsは確率0となり選ばれなくなる

    """

    def __init__(self):
        pass

    def process(self, logits, params):
        top_k = params.get("top_k", None)

        # logits が 1次元の torch.Tensor であることをチェックする
        if logits.dim() != 1:
            raise ValueError("logits tensor should be 1-dimensional.")

        min_num_of_tokens = 1  # トークンの最小個数

        if top_k is not None and top_k > 0:  # top_kがNoneでなく、0より大きい場合のみ処理を行う
            top_k = max(top_k, min_num_of_tokens)  # top_kの最小個数は担保されるようにする

            # top_kの値がlogitsの要素数よりも大きい場合に、top_kのほうをlogitsの要素数にあわせ制限する
            top_k = min(top_k, logits.size(0))
            logit_indice_to_be_set_small_values = logits < torch.topk(logits, top_k)[0][-1]  # top_k番目の値より小さいlogitsのインデックスを取得

            if logits.dtype == torch.float32:
                fill_value = -BIGGER_NUMBER_TO_FILTER_FP32
            elif logits.dtype == torch.float16:
                fill_value = -BIGGER_NUMBER_TO_FILTER_FP16
            else:
                raise ValueError(f"Unsupported dtype: {logits.dtype}")

            logits = logits.masked_fill(logit_indice_to_be_set_small_values, fill_value)  # 上記のインデックスのlogitsを-巨大数で置き換える
            # これで結果的に top_k 個のロジットは据え置かれ、それ以外のロジット(logit_indice_to_be_set_small_valuesで示されるインデックスの)
            # logitsの値を-BIGGER_NUMBER_TO_FILTER（負の巨大数）に設定する
            # 最後にsoftmax関数を適用するとき、負の無限大の値を持つlogitsは0の確率に変換されるため、選択されなくなる。

        return {"name": "TopKSampler", "type": "logits", "logits": logits}

    def get_name(self):
        return "top_k_sampling"
