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

import asyncio

import torch
from tokflow import SentenceStop

from chatstream.mock.chat_core_probe import ChatCoreProbe

# 停止文字列処理 定数
# "TOKFLOW" ... TokFlow パッケージを使用して停止文字列のマッチングをバッファリング処理する＝＞停止文字列の一部が開始されても表示されない。
# "SIMPLE"　... 停止文字列発見まで単純検索で探索する。＝＞停止文字列の一部が開始されたとき表示される。
STOP_STR_DETECTION_MODE = "TOKFLOW"  # "SIMPLE"  # SIMPLE / TOKFLOW

IS_CUT_OFF_REPLACEMENT_CHAR_AT_TAIL = True  # To address https://github.com/qualiteg/ChatStream/issues/29

# True: プローブモードが有効。現在のTokenizer,Modelへの入出力を記録しファイルに出力する。
# プローブモードについては右記issue参照のこと https://github.com/qualiteg/ChatStream/issues/34
# probe_mode_enabled = False

probe = ChatCoreProbe()


async def process_chat(model, tokenizer, token_sampler, device, params, chat_prompt):
    """
     指定された生成条件によって、文章生成を行う。

    事前学習済言語モデルによる並行トークン生成（非同期タスク）に対応。

    【文章生成について】
    文章生成は条件(params)によってモデルによる逐次文章生成をコントロールする
    また、停止ワードや停止トークンを監視し、必要なタイミングで文章生成を停止させる

    【複数のリクエストの並行処理について】
    FastAPIは非同期I/Oをサポートしており、これは複数のリクエストを並行に処理する能力がある。
    FastAPI（というかPythonの）非同期I/Oは、コルーチンと呼ばれる特殊な関数を使用して並行性を実現している。
    この場合の並行性とは、一度に一つのタスクだけが進行するが、I/O操作（HTTPリクエスト、モデルからのトークンの生成など）を待つ間に他のタスクを進行させることができる
    ということ。この形式を"協調的マルチタスク"を呼ぶ。
    それぞれのリクエストは別の「非同期タスク」として処理され、これらのタスクは同じスレッド上で切り替えられる。
    「非同期タスク」においては複数のリクエストに対するモデルへのアクセスが並行しているように見えるが
    実際にはある瞬間に一つのリクエストだけがモデルを利用している。
    そのため、それぞれのリクエストが　モデルによるトークン生成のためにブロックする期間は限られており、
    逐次出力トークンの生成について言えば、１つ新トークンを生成した後で他のリクエストに制御を戻すことができる。
    そのために、本メソッド内のforループ内で１つトークンを生成する毎に await asyncio.sleep(0) を呼び出し、
    他のタスクが進行できる（制御を移す）チャンスを与えるようにしている。
    そのため、一つのリクエストによる文章生成の際、停止トークン、停止文字列が現れるまでの間、
    他の全てのリクエストがブロックされることはなく、各リクエストはモデルからのトークンを逐次生成しながら、
    他のリクエストも進行させることができる。

    :param token_sampler:
    :param model:
    :param tokenizer:
    :param device:
    :param params:
            paramsの例
             {
    "temperature": 0.7,  # Temperatureの値
                             "max_new_tokens": 256,  # 新たに生成する最大トークンサイズ（何トークン分か。)
                             "context_len": 1024,  # コンテクストのサイズ（何トークン分か。)
                             "use_top_k_sampling": True,  # True: top K サンプリングを有効にする
                             "top_k_value": 50,  # top K サンプリングの値。
                             "use_top_p_sampling": True,  # True: top P サンプリングを有効にする
                             "top_p_value": 0.7,  # top P サンプリングの値
                             "use_repetition_penalty": False,  # True:繰り返し同じトークンを生成したときのペナルティを有効する
                             "repetition_penalty": 1,  # ペナルティの値
                             "repetition_penalty_method": "multiplicative"  # ペナルティの計算方法
             },
    :param chat_prompt:
    :return:
    """
    if token_sampler is None:
        raise ValueError("You must specify token_sampler")

    stream_interval = 1

    temperature = float(params.get("temperature", 1.0))
    max_new_tokens = int(params.get("max_new_tokens", 256))
    context_len = int(params.get("context_len", 1024))

    if chat_prompt.is_chat_mode_enabled():
        stop_strs = chat_prompt._get_final_stop_strs()
    else:
        stop_strs = None

    is_use_stop_strs = bool(stop_strs)

    sentence_stop = None
    sens_condition = None

    if is_use_stop_strs:
        if STOP_STR_DETECTION_MODE == "TOKFLOW":
            sentence_stop = SentenceStop(stop_strs)  # 1文を生成するごとに、SentenceStop をnewすることで初期化状態とする
            sens_condition = {"in_type": "full", "out_type": "full", "skip_existing_stop_str": True}

    force_set_bos_token_id = params.get("force_set_bos_token_id", None)
    force_set_eos_token_id = params.get("force_set_eos_token_id", None)

    add_special_tokens = params.get("add_special_tokens", None)

    use_top_k_sampling = params.get("use_top_k_sampling", True)
    top_k_value = params.get("top_k_value", None)

    use_top_p_sampling = params.get("use_top_p_sampling", True)
    top_p_value = params.get("top_p_value", 1.0)

    use_repetition_penalty = params.get("use_repetition_penalty", False)

    repetition_penalty = params.get("repetition_penalty", 1)

    repetition_penalty_method = params.get("repetition_penalty_method", "multiplicative")
    use_bos_for_input = params.get("use_bos_for_input", False)

    probe_mode_enabled = params.get("probe_mode_enabled", False)

    if force_set_bos_token_id:
        # patch for open_llama_7b_preview_300bt
        tokenizer.bos_token_id = force_set_bos_token_id

    if force_set_eos_token_id:
        # patch for open_llama_7b_preview_300bt
        stop_token_ids = params.get("stop_ids", [force_set_eos_token_id])
    else:
        stop_token_ids = params.get("stop_ids", [tokenizer.eos_token_id])

    prompt = chat_prompt.create_prompt()
    len_prompt = chat_prompt.get_skip_len()  # len(prompt) handled at issue #21

    if probe_mode_enabled:
        probe.set_tok_model(tokenizer, model, params)
        requester_message_text_list = [chat_content.get_message() for chat_content in chat_prompt.requester_messages]
        responder_message_text_list = [chat_content.get_message() for chat_content in chat_prompt.responder_messages]
        probe.set_input_texts(requester_message_text_list)
        probe.set_output_texts(responder_message_text_list)

    if use_bos_for_input:
        # force add bos
        input_ids = [tokenizer.bos_token_id] + tokenizer(prompt).input_ids
        len_prompt -= len(tokenizer.decode([tokenizer.bos_token_id]))
        if probe_mode_enabled:
            # Probeモードのとき、tokenizer.encode挙動を記録する
            probe.tok_call(prompt)
    else:
        if add_special_tokens is None:
            # tokenizer __call__ だと自動的に特殊トークンを入れてしまう模様.
            input_ids = tokenizer(prompt).input_ids
            if probe_mode_enabled:
                # Probeモードのとき、tokenizer.encode挙動を記録する
                probe.tok_call(prompt)
        else:
            # 特殊トークンを自動でいれさせないために add_special_token を明示的にマネージする
            input_ids = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
            if probe_mode_enabled:
                # Probeモードのとき、tokenizer.encode挙動を記録する
                probe.tok_encode(prompt, add_special_tokens)

    # 入力例
    # 語彙サイズが 32000 のモデルとする。
    # 入力テキスト：
    # 「タイタニックという映画を知っていますか？」
    # は以下のようにtokenizeされる
    # input_ids:
    # [6822, 276, 13856, 407, 4006, 362, 537, 28166, 18026, 392, 1615, 4506, 536, 583, 2680, 1013, 276, 263]
    output_token_ids = list(input_ids)

    max_src_len = context_len - max_new_tokens
    input_ids = input_ids[-max_src_len:]

    with torch.no_grad():
        for idx in range(max_new_tokens):

            # Insert asyncio.sleep(0) here to yield control after each token is generated
            await asyncio.sleep(0)

            logits_hash_on_probe_mode = None

            if idx == 0:
                # モデルに初回テンソルを入力して出力を得る
                # 初回は 入力テキストをトークンに変換した input_ids リストに格納されるトークン列を入力する
                out = model(input_ids=torch.as_tensor([input_ids], device=device), use_cache=True)
                # 入力例なら logits 形状は [1,18,32000] となる。[バッチサイズ,トークン列のサイズ,語彙サイズ]
                logits = out.logits

                past_key_values = out.past_key_values

                if probe_mode_enabled:
                    # Probeモードのとき、model.__call__挙動を記録する
                    # 戻り値 logits_hash_on_probe_mode はlast_token_logitsの「クローン」のハッシュ値。
                    # Mockモードでlogitsからtoken_idを取得するときのキーとして用いる。
                    # Mockモードでは乱数のからむサンプリングもスキップするためlogitsから確定的にtoken_idを取得するため
                    logits_hash_on_probe_mode = probe.model_call([input_ids], logits, past_key_values)


            else:
                # モデルに２回目以降テンソルを入力して出力を得る
                # ２回目以降はサンプリング関数を通して抽出された1件のトークン(token_id)を入力して継続するテキスト生成する
                out = model(
                    input_ids=torch.as_tensor([[token_id]], device=device),
                    use_cache=True,
                    past_key_values=past_key_values,  # ２回目以降は past_key_valueで過去の計算結果を入れているため、１トークンのみで効率的に生成できる
                )
                # 入力例なら logits 形状は [1,1,32000] となる
                logits = out.logits

                past_key_values = out.past_key_values

                if probe_mode_enabled:
                    # Probeモードのとき、model.__call__挙動を記録する
                    # 戻り値 logits_hash_on_probe_mode はlast_token_logitsの「クローン」のハッシュ値。
                    # Mockモードでlogitsからtoken_idを取得するときのキーとして用いる。
                    # Mockモードでは乱数のからむサンプリングもスキップするためlogitsから確定的にtoken_idを取得するため
                    logits_hash_on_probe_mode = probe.model_call([[token_id]], logits, past_key_values)

            # 最後のトークンに対して続きを生成するため、最後のロジットが重要であるため、最後のロジットを選ぶ
            # 最後のトークン用のロジットの形状は [32000]
            # ロジットとは、最終段の活性化関数に入れるまえのネットワークの出力値。
            # 32000個のトークンに１つずつにたいする出力値が格納される。
            # 活性化関数（ソフトマックス）で確率値に変換され、その確率値をサンプリング（ある条件で１つえらぶ）
            # して次に生成される単語に相当する１つのトークンが決定される。
            last_token_logits = logits[0][-1]

            if device == "mps":
                last_token_logits = last_token_logits.float().to("cpu")

            if not use_repetition_penalty:
                repetition_penalty = None

            # 最後のトークンのlogitsをサンプリングする
            token_id = token_sampler.do_sample(
                logits=last_token_logits,
                top_k=top_k_value if use_top_k_sampling else None,
                top_p=top_p_value if use_top_p_sampling else None,
                temperature=temperature,
                past_tokens=output_token_ids,
                penalty=repetition_penalty,
                penalty_method=repetition_penalty_method,
            )

            if probe_mode_enabled:
                # Probeモードのとき、sampling 挙動を記録する
                probe.sampler_do_sample(logits=last_token_logits,
                                        logits_hash=logits_hash_on_probe_mode,
                                        top_k=top_k_value if use_top_k_sampling else None,
                                        top_p=top_p_value if use_top_p_sampling else None,
                                        temperature=temperature,
                                        past_tokens=output_token_ids,
                                        penalty=repetition_penalty,
                                        penalty_method=repetition_penalty_method,
                                        token_id=token_id,

                                        )

            output_token_ids.append(token_id)

            stopped = False

            if token_id in stop_token_ids:
                stopped = True
            else:
                stopped = False

            if idx % stream_interval == 0 or idx == max_new_tokens - 1 or stopped:
                # skip_special_tokens = True で
                # tokenizer.special_tokens_map => {'bos_token': '<s>', 'eos_token': '</s>', 'unk_token': '<unk>'} など、特殊トークンをデコード結果に含めない
                output = tokenizer.decode(output_token_ids, skip_special_tokens=True)

                if probe_mode_enabled:
                    # Probeモードのとき、model.__call__挙動を記録する
                    probe.tok_decode(output_token_ids, output, skip_special_tokens=True)

                if IS_CUT_OFF_REPLACEMENT_CHAR_AT_TAIL:
                    if output and output.endswith("\uFFFD"):  # diamond-shaped question mark a.k.a REPLACEMENT CHARACTER
                        output = output[:-1]

                if is_use_stop_strs:
                    # モデルの停止文字列を定義している場合
                    if STOP_STR_DETECTION_MODE == "SIMPLE":
                        # 停止文字列のシンプル判定を使用するとき
                        for stop_str in stop_strs:
                            if stop_str:
                                pos = output.rfind(stop_str, len_prompt)
                                # print(f"output:'{output}' prompt:{prompt} len_prompt:{len_prompt} stop_str:{stop_str} pos:{pos}")
                                is_stop_str_found = (pos != -1)
                                if is_stop_str_found:
                                    output = output[:pos]
                                    stopped = True

                    elif STOP_STR_DETECTION_MODE == "TOKFLOW":
                        # 停止文字列を TokFlow の SentenceStop でバッファリングするモードのとき
                        sentence_stop_crr_result = sentence_stop.put(output, sens_condition)

                        crr_text_from_sentence_stop = sentence_stop_crr_result.get("text")

                        stop_str_found = sentence_stop_crr_result.get("stop_str_found", False)

                        output = crr_text_from_sentence_stop
                        if stop_str_found:
                            # 停止文字列が検出されたとき
                            stopped = True  # break するのでフラグ変更は本来不要だが SIMPLE モードとの関連のため残す
                            break

                yield output

            if stopped:
                break

        if is_use_stop_strs:
            if STOP_STR_DETECTION_MODE == "TOKFLOW":
                flushed_text_from_sentence_stop = sentence_stop.flush(sens_condition)
                output = flushed_text_from_sentence_stop
                yield output

        if probe_mode_enabled:
            probe.save()

    del past_key_values
