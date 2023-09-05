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

from chatstream.mock.mock_model import MockModel
from chatstream.mock.mock_token_sampler import MockTokenSampler
from chatstream.mock.mock_tokenizer import MockTokenizer


class MockTransformer:
    """
    HuggingFaceのTransformersライブラリのTokenizerとModelをエミューレートするクラス
    このクラスを用いることで、実際のTransformersライブラリを使わずに、モデルやトークナイザーの振る舞いを模倣することができる
    ・ただしシングルアクセスのみ。同時アクセスで使用すると、シード値が都度リセットされ、事前に想定した出力が得られない
    ・同時アクセスの負荷テストする場合は実際のモデルで行うこと

    Attributes:
    - parent_dir_path (str, optional): モデルとトークナイザーのデータを保存する親ディレクトリのパス。
    - dirname (str): モデルとトークナイザーのデータを保存するディレクトリの名前。
    """

    def __init__(self, dirname, parent_dir_path=None, wait_sec=None):
        """
        :param dirname: データを保存するディレクトリの名前。
        :type dirname: str
        :param parent_dir_path: モデルとトークナイザーのデータを保存する親ディレクトリのパス。デフォルトはNone。
        :type parent_dir_path: str, optional
        :param wait_sec １件生成にかかる時間のエミュレーションのためのウェイト時間

        """

        self.parent_dir_path = parent_dir_path
        self.dirname = dirname
        self.wait_sec = wait_sec

    def get_model(self):
        """
         MockModelのインスタンスを取得する。

         :return: MockModelのインスタンス。
         :rtype: MockModel
         """
        model = MockModel(dirname=self.dirname, parent_dir_path=self.parent_dir_path, wait_sec=self.wait_sec)
        return model

    def get_tokenizer(self):
        """
        MockTokenizerのインスタンスを取得する。

        :return: MockTokenizerのインスタンス。
        :rtype: MockTokenizer
        """
        tok = MockTokenizer(dirname=self.dirname, parent_dir_path=self.parent_dir_path)
        return tok

    def get_token_sampler(self):
        """
        TokenSamplerのインスタンスを取得する
        :return:
        """
        sampler = MockTokenSampler(dirname=self.dirname, parent_dir_path=self.parent_dir_path)
        return sampler
