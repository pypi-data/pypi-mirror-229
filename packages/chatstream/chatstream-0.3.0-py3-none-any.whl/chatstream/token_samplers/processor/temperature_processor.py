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
from chatstream.token_samplers.processor.logits_check_processor import LogitsCheckProcessor


class TemperatureProcessor(AbstractLogitsProcessor):
    """
    温度（temperature）に基づくlogitsの処理を行うクラス。

    ・温度が1より大きい場合（例: temperature = 1.5など）:

        出力の確率分布が「フラット」になる
        これは、低確率の出力も選択される可能性が増えるので、結果として、モデルの出力の多様性が増す
        一方で元の確率分布から逸脱する可能性も高まる

    ・温度が1より小さい場合（例: temperature = 0.5など）:
        出力の確率分布が「ピーク」を持ちやすくなる
        高確率の出力がさらに選択される可能性が増えることを意味するので、
    　　　結果として、モデルの出力は元の確率分布に従いやすくなり、
        予測がより確実になるが、多様性は失われる可能性がある

    ・温度が非常に低い場合（例: temperatureが1e-4未満）:
    　   最も確率の高い出力だけが選択されるようになる
    """

    def __init__(self):
        self.value_checker = LogitsCheckProcessor()

    def process(self, logits, params):
        temperature = params.get("temperature", 1)
        if temperature < 1e-4:
            token_id = int(torch.argmax(logits))
            return {"type": "token_id", "token_id": token_id}

        # 温度計算
        logits = logits / temperature

        # 不正値を適正化 (logits,temperatureの組み合わせによっては inf が発生する可能性があるため)
        logits = self.value_checker.process(logits, params).get("logits")

        return {"name": "TemperatureProcessor", "type": "logits", "logits": logits}

    def get_name(self):
        return "temperature"