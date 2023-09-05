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

import os
from datetime import datetime
import json
import torch
import uuid
import hashlib
from .mock_def import SAVE_LOGITS_INTO_ONE_FILE


class ChatCoreProbe:
    """
    TokenizerおよびModelの挙動をchat_core実行中にレコーディングし、
    TokenizerおよびModelへの入出力データをファイルに書きだすユーティリティ

    書きだされたデータは MockTransformer クラスによって復元され、
    MockModel および MockTokenizer として実際の huggingface 形式の
    Model/Tokenizer として振る舞い UT等で活用できる

    """

    def __init__(self, parent_dir_path=None):  # , chat_mode):
        self.seed = 42
        self.tokenizer = None
        self.model = None
        self.parent_dir_path = parent_dir_path
        self.save_path = self.get_path()

        self.last_token_ids = None

        self.dict_for_logits = {}
        self.dict_for_tokens = {
            "seed": None,
            "params": None,
            "tok_dict": {},
            "ids_to_logits_dict": {},
            "prompt_to_ids_dict": {},
            "ids_to_token_dict": {},
            "ids_to_token_dict_single": {},
            "logits_hash_to_token_id": {},
            "input_texts": [],  # ユーザーが入力したテキスト一覧
            "output_texts": [],  # アシスタントが出力したテキスト一覧（ただし、一番最後の出力は可能されない)
        }
        self.idx = 0

    def tensor_to_hash(self, tensor):
        # テンソルをバイトに変換
        tensor_bytes = tensor.cpu().numpy().tobytes()

        # SHA-256ハッシュを計算
        hash_obj = hashlib.sha256()
        hash_obj.update(tensor_bytes)
        hex_dig = hash_obj.hexdigest()

        return hex_dig

    def get_path(self, dirname=None):
        # Build the full path

        # 現在の日時を取得
        now = datetime.now()

        # YYYYmmdd_hhmmss 形式にフォーマット
        formatted_time = now.strftime('%Y%m%d_%H%M%S')

        if self.parent_dir_path:

            if dirname is None:
                probe_data_path = os.path.join(self.parent_dir_path, formatted_time)
            else:
                probe_data_path = os.path.join(self.parent_dir_path, dirname)
        else:
            home_dir = os.path.expanduser("~")
            if dirname is None:
                probe_data_path = os.path.join(home_dir, ".cache", "chatstream", "probe_data", formatted_time)
            else:
                probe_data_path = os.path.join(home_dir, ".cache", "chatstream", "probe_data", dirname)

        return probe_data_path

    def set_tok_model(self, tokenizer, model, params):
        """
        元のtokenizer,model,seed値をセットする
        :param tokenizer:
        :param model:
        :param seed:
        :return:
        """
        self.tokenizer = tokenizer
        self.model = model
        self.dict_for_tokens["seed"] = params.get("seed", None)
        self.dict_for_tokens["params"] = params

        data_dict = {
            "special_tokens": tokenizer.special_tokens_map,
            "bos_token_id": tokenizer.bos_token_id,
            "eos_token_id": tokenizer.eos_token_id,
            "pad_token_id": tokenizer.pad_token_id,
            "unk_token_id": tokenizer.unk_token_id,
            #
            "bos_token": tokenizer.bos_token,
            "eos_token": tokenizer.eos_token,
            "pad_token": tokenizer.pad_token,
            "unk_token": tokenizer.unk_token,
        }

        os.makedirs(self.save_path, exist_ok=True)
        self.dict_for_tokens["tok_dict"] = data_dict

    def set_input_texts(self, texts):
        self.dict_for_tokens["input_texts"] = texts

    def set_output_texts(self, texts):
        """
        AIアシスタントが出力したテキストを保存する
        （chat_coreの仕組み上、一番最後の出力は保存されずnullが格納される)
        :param texts:
        :return:
        """
        self.dict_for_tokens["output_texts"] = texts

    def list_to_string(self, lst):
        """
        list => str 変換をする

        使用例
        lst = [1, 2, 3]
        result = list_to_string(lst)
        print(result)  => "1_2_3"

        :param lst:
        :return:
        """
        return "_".join(map(str, lst))

    def model_call(self, input, logits, past_key_values):
        """
        ある入力token_idから生成されるlogitsを記録する
        :param input:
        :param logits:
        :param past_key_values:
        :return:
        """
        input_ids = input[0]
        input_ids_merged_str = self.list_to_string(input_ids)
        if len(input_ids) == 1:
            # 1件のみのトークン入力のとき
            # 過去のトークンIDを連結したキーを生成する
            # 一連の連結されたトークン文字列により、現在の１個のトークンの一意性を担保する。
            # 別のシチュエーションで同じトークンIDが生成されても、現在とそのときで会話コンテクストは当然異なるため
            # １件のトークンだとしても、一意性を担保する必要がある
            input_ids_merged_str = f"{self.last_token_ids}_{input_ids_merged_str}"
            self.last_token_ids = input_ids_merged_str
        else:
            # 複数件のトークン入力のとき
            # 複数件ある場合は、１件の文章生成の開始時となる
            self.last_token_ids = input_ids_merged_str

        ids_to_logits_dict = self.dict_for_tokens.get("ids_to_logits_dict")

        last_input_id = input_ids[-1]
        logit_uid = f"{last_input_id}__{uuid.uuid4()}"
        logits_filename = f"logits-{logit_uid}.pt"
        ids_to_logits_dict[input_ids_merged_str] = logits_filename

        # 必要な部分だけを取得
        relevant_logits = logits[0][-1].clone()
        logits_hash = self.tensor_to_hash(relevant_logits)

        if SAVE_LOGITS_INTO_ONE_FILE:
            # logitsをまとめて１ファイルに保存するモード
            self.dict_for_logits[logits_filename] = relevant_logits
        else:
            # 1件ずつlogitsを保存するモード
            file_path = os.path.join(self.save_path, logits_filename)
            torch.save(relevant_logits, file_path)
        return logits_hash

    def tok_encode(self, prompt, add_special_tokens):
        """
        tokenizer.encode(prompt,add_special_tokens) の実行を記録する
        :param prompt:
        :param add_special_tokens:
        :return:
        """
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=add_special_tokens)

        prompt_to_ids_dict = self.dict_for_tokens.get("prompt_to_ids_dict")
        prompt_to_ids_dict[prompt] = {"ids": input_ids, "add_special_tokens": add_special_tokens, "type": "encode"}

        if len(prompt_to_ids_dict) == 1:
            # 初回の登録の場合
            prompt_to_ids_dict[prompt]["is_first"] = True

    def tok_call(self, prompt):
        """
        tokenizer(prompt) の実行を記録する
        :param prompt:
        :return:
        """
        input_ids = self.tokenizer(prompt).input_ids
        # こんにちは -> [1,2,3] をひもづける
        prompt_to_ids_dict = self.dict_for_tokens.get("prompt_to_ids_dict")
        prompt_to_ids_dict[prompt] = {"ids": input_ids, "type": "call"}
        if len(prompt_to_ids_dict) == 1:
            # 初回の登録の場合
            prompt_to_ids_dict[prompt]["is_first"] = True

    def tok_decode(self, output_token_ids, output, skip_special_tokens=True):
        """
        tokenizer.decode(ids) の実行を記録する
        :param output_token_ids:
        :param output:
        :param skip_special_tokens:
        :return:
        """
        # [1,2,3] みたいな出力と['あ','い','う']をひもづける
        ids_to_token_dict = self.dict_for_tokens.get("ids_to_token_dict")
        ids_to_token_dict_single = self.dict_for_tokens.get("ids_to_token_dict_single")
        key_ids = self.list_to_string(output_token_ids)
        ids_to_token_dict[key_ids] = output

        if True:
            # 注意
            # トークン1件ずつのデコードと、複数のトークンからなるトークン列のデコードは結果が異なることがあるので注意
            # 特定のトークナイザでは、複数のトークンをまとめてデコードすると、適切なスペースや区切りを考慮して文字列を再構築しようとする
            # これに対して、トークンを一つずつデコードすると、そのような最適化は行われない。
            # そのため、トークンを１件ずつデコードして、トークンID→単語　のような辞書を作り、その辞書をつかってトークン列（複数トークン）
            # のデコードを行うような処理を行わないこと
            # 以下のロジックは参考データとして残しておくが、トークン列のデコードには使用しないこと。
            for token_id in output_token_ids:
                word = self.tokenizer.decode([token_id], skip_special_tokens=skip_special_tokens)
                if token_id in ids_to_token_dict_single:
                    continue
                ids_to_token_dict_single[token_id] = word

    def sampler_do_sample(self, logits, logits_hash, top_k=None, top_p=None, temperature=1.0, past_tokens=None, penalty=None, penalty_method="multiplicative",
                          token_id=None):
        # hash_str = self.tensor_to_hash(logits) # 直接ハッシュ値を計算せず、与えられたハッシュ値を採用する
        logits_hash_to_token_id = self.dict_for_tokens.get("logits_hash_to_token_id")
        logits_hash_to_token_id[logits_hash] = token_id  # token_sampler の挙動を記録する

    def save(self):
        """
        レコーディングしたデータを保存する
        :return:
        """

        file_path_tokens = os.path.join(self.save_path, "tokens.json")
        file_path_logits = os.path.join(self.save_path, "logits.pt")

        # tokens.json をファイルとして保存する
        with open(file_path_tokens, 'w', encoding='utf-8') as f:
            json.dump(self.dict_for_tokens, f, ensure_ascii=False, indent=2)

        if SAVE_LOGITS_INTO_ONE_FILE:
            # logitsをまとめて１ファイルに保存するモード
            torch.save(self.dict_for_logits, file_path_logits)
        else:
            # 1件ずつlogitsを保存するモード
            pass

        # 保存は１回の文章生成のタイミングで呼び出される想定であるため
        # 次の入力、出力ペアにそなえ、last_idsはクリアする
        self.last_token_ids = None
