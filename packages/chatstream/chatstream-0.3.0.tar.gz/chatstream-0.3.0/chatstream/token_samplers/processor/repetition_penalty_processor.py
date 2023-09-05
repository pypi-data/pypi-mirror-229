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
from chatstream.token_samplers.logits_processor import AbstractLogitsProcessor


class RepetitionPenaltyProcessor(AbstractLogitsProcessor):
    """
    繰り返しのトークンに対してペナルティを適用するプロセッサ。

    このクラスは、過去に使用されたトークンのlogitsを調整することで、繰り返しの出現を抑制する。
    ペナルティの適用方法は、乗算または減算のいずれかで、パラメータで指定できる。

    乗算ペナルティ計算の基本は　logits[token_id] /= penalty　で、過去に出現した token_id のロジット値を減らしていき
    出現確率を下げることで繰り返し同じトークンが出力されることを抑制する

    """

    def __init__(self):
        pass

    def process(self, logits, params):

        past_tokens = params.get("past_tokens", None)
        penalty = params.get("penalty", None)
        penalty_method = params.get("penalty_method", "multiplicative")

        # 過去のトークンのlogitsにペナルティを適用
        if penalty is not None and past_tokens is not None:
            # logitsのコピーを作成(引数として渡されたlogitsの非破壊保証)
            adjusted_logits = logits.clone()
            # penaltyの値の型を確認する
            if not isinstance(penalty, (int, float)):
                raise ValueError(f"penalty should be a scalar value, but got {penalty}({type(penalty)})")

            # ペナルティの適用方法に応じてlogitsを更新する
            if penalty_method == "multiplicative":
                if penalty != 1.0:
                    for token_id in set(past_tokens):
                        adjusted_logits[token_id] /= penalty

            elif penalty_method == "subtractive":
                for token_id in set(past_tokens):
                    adjusted_logits[token_id] -= penalty
            else:
                raise ValueError(f"Unknown penalty_method: {penalty_method}")
        else:
            adjusted_logits=logits

        return {"name": "RepetitionPenaltyProcessor", "type": "logits", "logits": adjusted_logits}


    def get_name(self):
        return "rep_penalty"