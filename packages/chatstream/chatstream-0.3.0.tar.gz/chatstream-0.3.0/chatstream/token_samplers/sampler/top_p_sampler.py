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


class TopPSampler(AbstractLogitsProcessor):
    """
    top_p サンプリングを行う

    top_p, もしくは nucleus sampling は、
    トークンの生成確率を１つずつ足していった累積和が指定した閾値（たとえば、top_p=0.9 の場合は 90%)に達するまでのトークンのみを考慮する手法

    ・まずlogitsをソートしてsoftmaxで確率分布にする
    　例えばSoftmax後の確率分布が [0.5, 0.3, 0.07, 0.05, 0.03,...]だったとき累積和を求めると以下のようになる。
      0.5 (0.5)
      0.8 (0.5+0.3)
      0.87 (0.5+0.3+0.07)
      0.92 (0.5+0.3+0.07+0.05)
      この計算は torch.cumsumで行える。torch.cumsum の結果は [0.5 0.8 0.87 0.92 ...] のようになる
      このとき 0.92 で top_p である 0.9 を超えるため、
      top_p サンプリングで考慮にいれるのは [0.5 0.3 0.07]の確率をもつトークンであるということ。
      それ以外の確率（のもととなるロジット）は強制的に極小値をセットし最後のsoftmaxしたとき0にちかい値になるようにして、
      選択されないようにする。

      確率分布によっては top_p サンプリングによってかなり広い範囲のトークンまでひろうことになり、
      確率の低いトークンを出力する事になる場合もある。
      top_k によって選び出されたロジットに対してtop_pを適用するとバランスが良くなる場合がある。
      top_k => top_p という順序でフィルターするとき、
      top_kの値があまりにも小さいときは、top_kによって抽出されたロジットのsoftmax後の確率値が
      すべて足し合わせても top_p の閾値を超えないことはありうる。
      その場合、実質、top_pは効力をはっきしていない状態となる。
      top_k ,top_p を同時に使用するときは、両フィルタリングがうまく機能しているバランスをとると効果的となる。
      その際、出力されるテキストだけでなく、複数の文章生成でロジット、確率分布をモニタリングし、
      良いバランスでフィルターされているかどうか確認することでより良質な出力を得ることができる。
    """

    def __init__(self):
        pass

    def process(self, logits, params):

        top_p = params.get("top_p", None)

        # logits が 1次元の torch.Tensor であることをチェックする
        if logits.dim() != 1:
            raise ValueError("logits tensor should be 1-dimensional.")

        if top_p is not None and (0 <= top_p < 1.0):
            # 条件が合致した場合にlogitsのコピーを作成
            logits_copy = logits.clone()

            sorted_logits, sorted_indices = torch.sort(logits_copy, descending=True)

            probs = torch.softmax(sorted_logits, dim=-1)
            cumulative_probs = torch.cumsum(probs, dim=-1)
            sorted_indices_to_remove = cumulative_probs > top_p

            # logits.dtypeに基づいてBIGGER_NUMBER_TO_FILTERの値を選択
            if logits.dtype == torch.float32:
                fill_value = -BIGGER_NUMBER_TO_FILTER_FP32
            elif logits.dtype == torch.float16:
                fill_value = -BIGGER_NUMBER_TO_FILTER_FP16
            else:
                raise ValueError(f"Unsupported dtype: {logits.dtype}")

            # logits_copyの配列を更新する
            logits_copy[sorted_indices[sorted_indices_to_remove]] = fill_value

            return {"name": "TopPSampler", "type": "logits", "logits": logits_copy}

        # top_pの条件に合致しない場合は、元のlogitsをそのまま返す
        return {"name": "TopPSampler", "type": "logits", "logits": logits}

    def get_name(self):
        return "top_p_sampling"

