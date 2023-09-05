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


class SoftmaxSampler(AbstractLogitsProcessor):
    """
    logits にSoftmax 処理を行い、1件のトークンをサンプリングする
    """

    def __init__(self):
        pass

    def process(self, logits, params):
        # logits が 1次元の torch.Tensor であることをチェックする
        if logits.dim() != 1:
            raise ValueError("logits tensor should be 1-dimensional.")

        # logitsを確率分布に変換
        probabilities = torch.nn.functional.softmax(logits, dim=-1)

        # 確率分布からサンプリング
        token_id = torch.multinomial(probabilities, 1).item()

        return {"name": "SoftmaxSampler", "type": "token_id", "token_id": token_id, "probabilities": probabilities}

    def get_name(self):
        return "softmax"