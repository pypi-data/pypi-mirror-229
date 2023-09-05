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

import json
import os
import time

import torch

from chatstream.mock.chat_core_probe import ChatCoreProbe
from .mock_def import SAVE_LOGITS_INTO_ONE_FILE


class MockModelOutput:
    def __init__(self, logits, past_key_values):
        """
        モックモデルの出力をシミュレートするためのクラス。

        :param logits: モデルの出力ロジット
        :type logits: torch.Tensor
        :param past_key_values: 過去のキーと値のペア（このモックモデルでは未使用）
        """

        self.logits = logits
        self.past_key_values = past_key_values


class MockModel:
    def __init__(self, dirname, parent_dir_path=None, wait_sec=None):
        """
         HuggingFace Transformers の Model をエミュレーションするためのモッククラス。

         :param dirname: ディレクトリ名
         :type dirname: str
         :param parent_dir_path: 親ディレクトリのパス（オプション）無指定の場合 [home_dir]/.cache/chatstream/probe_data がセットされる
         :type parent_dir_path: str, optional
         :param wait_sec: １件の生成で何秒ウェイトを入れるかを「秒」で設置絵する（オプション）
         :type wait_sec: int, optional
         """

        self.probe = ChatCoreProbe(parent_dir_path)

        self.save_path = self.probe.get_path(dirname=dirname)

        self.my_dict = None

        self.loaded_logits_dict = None

        self.wait_sec = wait_sec

        with open(os.path.join(self.save_path, "tokens.json"), 'r', encoding='utf-8') as file:
            self.my_dict = json.load(file)

        if SAVE_LOGITS_INTO_ONE_FILE:
            file_path = os.path.join(self.save_path, "logits.pt")  # logits_filename
            self.loaded_logits_dict = torch.load(file_path)  # logit データの state_dict をキャッシュ

    def to(self, device):
        """
        デバイスへモデルを移動するためのダミーメソッド。
        """
        pass

    def half(self):
        """
        モデルの重みを半精度浮動小数点数に変換するためのダミーメソッド。
        """
        pass

    def eval(self):
        """
        モデルを評価モードに設定するためのダミーメソッド。
        """
        pass

    def tensor_to_list(self, data):
        """
         Tensor をリストに変換するメソッド。

         :param data: 入力データ
         :type data: torch.Tensor or list
         :return: リストに変換されたデータ
         :rtype: list or None
         """
        if isinstance(data, torch.Tensor):
            return data.cpu().numpy().tolist()
        elif isinstance(data, list):
            return data
        else:
            print("Input is neither a PyTorch tensor nor a list.")
            return None

    def __call__(self, input_ids, use_cache, past_key_values=None):
        """
        モデルを呼び出すためのメソッド。

        :param input_ids: 入力 ID
        :type input_ids: torch.Tensor
        :param use_cache: キャッシュを使用するかどうか
        :type use_cache: bool
        :param past_key_values: 過去のキーと値のペア（オプション）
        :type past_key_values: any, optional
        :return: モックモデルの出力
        :rtype: MockModelOutput
        """
        # ここで3秒待機

        if self.wait_sec:
            time.sleep(self.wait_sec)

        # input_ids が tensorならリストに変換
        input_ids = self.tensor_to_list(input_ids[0])

        # input_ids=[1,2,3] のとき "1_2_3" に変換する。
        # input_ids=[1] のとき "1" に変換する。
        input_ids_str = self.probe.list_to_string(input_ids)

        if len(input_ids) == 1:
            # input_idsリストのサイズが1のとき、A.文章生成におけるループ2回目以降　または　B.チャット入力で「あ」だけ入れるなど１トークンぶんだけいれたときのループ1回目。
            if past_key_values is not None:
                # past_key_values が None でないとき　→　Aのパターンの場合
                history_of_ids_str = f"{past_key_values}_{input_ids_str}"  # これまで生成されたtoken_idをマージして、生成履歴のチェーンをつくる

            else:
                # B.チャット入力で「あ」だけ入れるなど１トークンぶんだけいれたときのループ1回目。のパターンとき
                history_of_ids_str = input_ids_str

        else:
            # input_idsリストのサイズが2以上のとき
            # token_id が複数件入力された場合は初回と判定する
            history_of_ids_str = input_ids_str  #

        ids_to_logits_dict = self.my_dict.get("ids_to_logits_dict")

        logits_filename = ids_to_logits_dict.get(history_of_ids_str)

        if SAVE_LOGITS_INTO_ONE_FILE:

            # logitsをまとめて１ファイルに保存するモード
            logits = self.loaded_logits_dict[logits_filename]
        else:
            # 1件ずつlogitsを保存するモード
            file_path = os.path.join(self.save_path, logits_filename)

            logits = torch.load(file_path)  # この時点で形状は[語彙サイズ]

        # 形状を [1, 1, 語彙サイズ] に変更。 last_token_logits = logits[0][-1]としてアクセスできるように
        logits = logits.unsqueeze(0).unsqueeze(0)

        return MockModelOutput(logits=logits, past_key_values=history_of_ids_str)
