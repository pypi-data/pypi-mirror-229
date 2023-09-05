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
from .softmax_sampler import SoftmaxSampler
from ..logits_processor import AbstractLogitsProcessor


class IsolatedTopKSampler(AbstractLogitsProcessor):
    def __init__(self):
        self.softmax_sampler = SoftmaxSampler()

    def process(self, logits, params):

        """
        Isolated な top_k サンプリングを行う。当SamplerはSofmax つきで、当サンプラーが最終的な token_id まで返す

        【この計算方法の特徴】
        logits から上位 top_k 個の logits だけを取り上げてその中でサンプリングを行う
        すなわち全体のlogitsの中でのtop_kの相対的な大小は考慮せずに top_k個のlogits内でのみsoftmaxが適用されてサンプリングを行う
        この手法はやや極端だが一部の「日本語」モデルと相性が良いことがQualitegの実験で判明した。

        一方、標準的なtop_kサンプリングでは、logitsの中から最も高いk個の値をキープしつつ、
        他のlogitsを無限小あるいは非常に低い値にする。
        そして、そのlogitsにsoftmaxを適用して確率分布を得る。

        本手法と一般的な手法の主な違いは、top_k個以外の値を小さくしつつもlogits全体からサンプルするか、
        top_k個以外は完全ムシしてtop_k個の世界だけからサンプルするか、となる。

        :param logits: モデルの生の出力を示す1次元のテンソル。
        :type logits: torch.Tensor (1次元テンソル)

        :param top_k: 指定された場合、サンプリングはtop_kのlogitsに制限されます。デフォルトはNone。
        :type top_k: Optional[int]

        :return: サンプルされたトークンID。
        :rtype: int
        """
        top_k = params.get("top_k", None)

        # logits が 1次元の torch.Tensor であることをチェックする
        if logits.dim() != 1:
            raise ValueError("logits tensor should be 1-dimensional.")

        min_num_of_tokens = 1  # トークンの最小個数
        if top_k is not None:

            top_k = max(top_k, min_num_of_tokens)  # top_kの最小個数は担保されるようにする

            # top_kの値がlogitsの要素数よりも大きい場合に、top_kのほうをlogitsの要素数にあわせ制限する
            top_k = min(top_k, logits.size(0))

            top_k = torch.topk(logits, top_k)  # logitsの中で最も大きいtop_k個の値とそれらの値のlogits内でのインデックスを返す
            top_k_indices = top_k.indices  # logits内でのインデックスを返す
            top_k_values = top_k.values

            probabilities_on_top_k_values = torch.softmax(top_k_values, dim=-1)  # 確率分布に変換

            # probabilities = torch.tensor([0.1, 0.5, 0.4]) であれば、
            # torch.multinomial(probs, 1)を呼び出すと、
            # 10%の確率でインデックス0
            # 50%の確率でインデックス1
            # 40%の確率でインデックス2を、を返す
            index_on_top_k_values = torch.multinomial(probabilities_on_top_k_values, num_samples=1)  # top_k_valuesの確率分布から１つ選択。
            # choiceは top_k個のなかのインデックスなので、これをlogits全体の内のインデックス＝token_id に変換する
            token_id = int(top_k_indices[index_on_top_k_values])
            return {"type": "token_id", "token_id": token_id, "top_k_indices": top_k_indices, "logits": top_k_values,
                    "probabilities": probabilities_on_top_k_values}

        else:
            # top_k が無いとき

            # 通常のsoftmax=>サンプル処理
            result = self.softmax_sampler.process(logits, params)
            token_id = result.get("token_id")
            probabilities = result.get("probabilities")

            return {"name": "IsolatedTopKSampler", "type": "token_id", "token_id": token_id, "probabilities": probabilities}

    def get_name(self):
        return "isolated_top_k_sampling_softmax"