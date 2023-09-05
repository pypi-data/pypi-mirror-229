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


class LogitsCheckProcessor(AbstractLogitsProcessor):
    """
    logitsの中の異常な値（NaNや無限大）を適切な値に修正するプロセッサ。

    このクラスは、logitsにNaNや無限大のような計算上問題のある値が存在する場合、
    それらの値を適切な値で置き換えることで、計算を正常に進行させる。

    """

    def __init__(self):
        pass

    def process(self, logits, params):
        # logitsに異常な値がないか確認する
        if torch.any(torch.isnan(logits)) or torch.any(torch.isinf(logits)):
            # NaNやInfの値を適切な値に置き換える

            # logitsの中にNaN（Not a Number）の値が存在する場合、その位置の値を0で置き換える
            logits = torch.where(torch.isnan(logits), torch.full_like(logits, 0), logits)

            # logitsの中で正の無限大の値が存在する場合、このままだと計算が続行不能になるので
            # 計算をつづけられるようにするため、このデータ型(dtype)の最大値で置き換える
            logits = torch.where(torch.isinf(logits) & (logits > 0),
                                 torch.full_like(logits, torch.finfo(logits.dtype).max),
                                 logits)

            # こちらはlogitsの中で負の無限大の値が存在する場合、このままだと計算が続行不能になるので
            # 計算をつづけられるようにするため、このデータ型(dtype)の最小値で置き換える
            logits = torch.where(torch.isinf(logits) & (logits < 0),
                                 torch.full_like(logits, torch.finfo(logits.dtype).min),
                                 logits)

        return {"name": "LogitsCheckProcessor", "type": "logits", "logits": logits}

    def get_name(self):
        return "check"
