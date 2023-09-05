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

from chatstream.mock.chat_core_probe import ChatCoreProbe


class MockTokenSampler:

    def __init__(self, dirname, parent_dir_path=None):
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

        # JSONファイルを読み込む
        with open(os.path.join(self.save_path, "tokens.json"), 'r', encoding='utf-8') as file:
            self.my_dict = json.load(file)

    def do_sample(self, logits, top_k=None, top_p=None, temperature=1.0, past_tokens=None, penalty=None, penalty_method="multiplicative"):
        hash_str = self.probe.tensor_to_hash(logits)

        logits_hash_to_token_id = self.my_dict.get("logits_hash_to_token_id")
        token_id = logits_hash_to_token_id.get(hash_str)

        return token_id
