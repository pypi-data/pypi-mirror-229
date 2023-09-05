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

from .processor.logits_check_processor import LogitsCheckProcessor
from .processor.repetition_penalty_processor import RepetitionPenaltyProcessor
from .processor.temperature_processor import TemperatureProcessor
from .sampler.isolated_top_k_softmax_sampler import IsolatedTopKSampler
from .sampler.softmax_sampler import SoftmaxSampler
from .sampler.top_k_sampler import TopKSampler
from .sampler.top_p_sampler import TopPSampler


class TokenSamplerBuilder:
    """
    トークンのサンプリングの前処理をまとめるビルダークラス。

    このクラスは、トークンのサンプリングに関連するさまざまな前処理を効率的に実行するためのもので、
    事前に定義されたプロセッサを順番に実行することができる。

     Methods
    -------
    process(logits, params) -> Union[torch.Tensor, int]
        登録されているプロセッサを使用してlogitsの前処理を行い、結果を返す。
        params["result_type"]= "dict" を指定した場合、結果を dictとして返す。（検証用)

    append(name) -> 'TokenSamplerBuilder'
        指定された名前のプロセッサをprocessorsのリストに追加する。利用可能なプロセッサの名前は以下の通り：
        - "check": LogitsCheckProcessor - NaNやInfのlogits値を適切に置き換える。
        - "rep_penalty": RepetitionPenaltyProcessor - 繰り返しのペナルティを適用する。
        - "temperature": TemperatureProcessor - logitsにテンパレチャー調整を適用する。
        - "top_k": TopKSampler - top-kサンプリング。
        - "top_p": TopPSampler - top-pサンプリング (nucleus sampling)。
        - "isolated_top_k_sampling_softmax": IsolatedTopKSampler - isolated top-kサンプリング+softmaxサンプリング。
        - "softmax": SoftmaxSampler - 通常のsoftmaxによるサンプリング。

    Examples
    --------
    >>> builder = TokenSamplerBuilder()
    >>> builder.append("check").append("rep_penalty")
    """

    def __init__(self):
        self.processors = []

    def process(self, logits, params):
        # 複数のプロセッサーを順番に実行し、結果を返す
        # 最後に softmax系プロセッサをappendして使用することを想定しており、softmax系プロセッサをappendすることで本メソッドの
        # 戻り値は token_id となる。
        # softmax系プロセッサを使用しない場合戻り値は、それまでのプロセッサの最終計算結果 logits となる
        # params["result_type"]="dict"に指定した場合、
        # 動作検証モードとなり戻り値となるdictに"process_history"パラメータとして各々のプロセッサの途中演算結果が履歴として格納される
        on_going_logits = logits

        result_type = params.get("result_type", "value")
        each_result_list = []
        ret_value = None
        for proc in self.processors:
            result = proc.process(on_going_logits, params)
            each_result_list.append(result)
            return_type = result.get("type")

            if return_type == "logits":
                on_going_logits = result.get("logits")

                if result_type == "value":
                    ret_value = on_going_logits
                else:
                    ret_value = {"type": "logits", "logits": on_going_logits, "process_history": each_result_list}  # 中途で終了した場合に戻す値

            elif return_type == "token_id":
                token_id = result.get("token_id")
                probabilities = result.get("probabilities", None)  # softmax の場合,softmax結果

                if result_type == "value":
                    return token_id
                else:
                    return {"type:": "token_id", "token_id": token_id, "probabilities": probabilities, "process_history": each_result_list}


            else:
                raise ValueError(f"Unknown return_type:'{return_type}'")

        return ret_value

    def append(self, name):
        if name == "check":
            lcp = LogitsCheckProcessor()
            self.processors.append(lcp)
        elif name == "rep_penalty":
            rpp = RepetitionPenaltyProcessor()
            self.processors.append(rpp)
        elif name == "temperature":
            tp = TemperatureProcessor()
            self.processors.append(tp)
        elif name == "top_k_sampling":
            tks = TopKSampler()
            self.processors.append(tks)
        elif name == "top_p_sampling":
            tps = TopPSampler()
            self.processors.append(tps)
        elif name == "isolated_top_k_sampling_softmax":
            itks = IsolatedTopKSampler()
            self.processors.append(itks)
        elif name == "softmax":
            ss = SoftmaxSampler()
            self.processors.append(ss)
        else:
            raise ValueError(f"Unknown processor name:'{name}' Please specify valid processor name.")

        return self
