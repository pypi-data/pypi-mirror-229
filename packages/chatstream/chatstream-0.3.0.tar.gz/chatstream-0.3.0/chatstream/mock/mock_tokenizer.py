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

from chatstream.mock.chat_core_probe import ChatCoreProbe
from transformers import set_seed

import json
import os


class MockTokenizer:
    """
    HuggingFace Transformers の Model のトークナイザをエミュレートするクラス。

    :param dirname: トークンデータが格納されているディレクトリ名
    :param parent_dir_path: 親ディレクトリのパス（オプション）無指定の場合 [home_dir]/.cache/chatstream/probe_data がセットされる
    """

    def __init__(self, dirname, parent_dir_path=None):
        """
        インスタンスを初期化し、トークンデータを読み込む。

        :param dirname: トークンデータが格納されているディレクトリ名
        :param parent_dir_path: 親ディレクトリのパス（オプション）無指定の場合 [home_dir]/.cache/chatstream/probe_data がセットされる
        """
        self.probe = ChatCoreProbe(parent_dir_path)
        save_path = self.probe.get_path(dirname=dirname)
        self.my_dict = None

        # JSONファイルを読み込む
        with open(os.path.join(save_path, "tokens.json"), 'r', encoding='utf-8') as file:
            self.my_dict = json.load(file)

        tok_dict = self.my_dict["tok_dict"]

        self.special_tokens_map = tok_dict.get("special_tokens")
        self.bos_token_id = tok_dict.get("bos_token_id")
        self.eos_token_id = tok_dict.get("eos_token_id")
        self.pad_token_id = tok_dict.get("pad_token_id")
        self.unk_token_id = tok_dict.get("unk_token_id")
        self.bos_token = tok_dict.get("bos_token")
        self.eos_token = tok_dict.get("eos_token")
        self.pad_token = tok_dict.get("pad_token")
        self.unk_token = tok_dict.get("unk_token")

    def __call__(self, text):
        """
        オブジェクトが関数として呼ばれたときの動作を定義。
        テキストをエンコードしてMockInputオブジェクトを返す。

        :param text: エンコードするテキスト
        :return: MockInputオブジェクト
        """
        ids = self.encode(text)
        return MockInput(ids=ids)

    def encode(self, text, add_special_tokens=False):
        """
        テキストをエンコードし、token_id のリストを返す。

        :param text: エンコードするテキスト
        :param add_special_tokens: 特殊トークンを追加するかどうかのフラグ
        :return: エンコードされたIDのリスト
        """
        prompt_to_ids_dict = self.my_dict["prompt_to_ids_dict"]
        seed = self.my_dict.get("params").get("seed")

        ids_data = prompt_to_ids_dict.get(text)
        if ids_data is None:
            raise ValueError(f"Prompt '{text}' is not found in mock tokenizer.")

        ids = ids_data.get("ids")

        is_first = ids_data.get("is_first", False)

        if is_first:
            # - 初回に呼び出される想定のプロンプトが入力されたとき
            # 同じプロンプトでも、生成回数が増えるにつれ乱数が変化するため異なる応答が生成されてしまう
            # 初回に呼び出される想定のプロンプトが来た場合、シードリセットし初期状態を復活させる
            if seed:
                set_seed(seed)

        add_special_tokens_ = ids_data.get("add_special_tokens")

        if add_special_tokens is not add_special_tokens_:
            raise ValueError(f"Prompt '{text}' 's add_special_tokens is not match. stored:{add_special_tokens_} actual:{add_special_tokens}")

        return ids

    def decode(self, token_ids, skip_special_tokens=True):
        """
        token_idをデコードしてテキストを返す。

        :param token_ids: デコードするトークンIDのリスト
        :param skip_special_tokens: 特殊トークンをスキップするかどうかのフラグ
        :return: デコードされたテキスト
        """
        # output_token_ids, skip_special_tokens = True
        ids_to_token_dict = self.my_dict.get("ids_to_token_dict")
        token_ids_str = self.probe.list_to_string(token_ids)
        decoded = ids_to_token_dict.get(token_ids_str)

        if decoded is None:
            raise ValueError(f"token_ids_str '{token_ids_str}' is not found in ids_to_token_dict. MockModelで動作させているときにchat_coreをPROBE_MODEを使っていないか確認ください。")

        return decoded


class MockInput:
    """
    MockTokenizer からの入力として使用されるクラス。

    :param ids: 入力token_id
    """

    def __init__(self, ids):
        """
        インスタンスを初期化する。

        :param ids: 入力ID
        """
        self.input_ids = ids
