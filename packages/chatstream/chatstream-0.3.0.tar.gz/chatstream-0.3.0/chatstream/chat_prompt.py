from abc import ABC, abstractmethod

from enum import Enum, auto


class RoleType(Enum):
    REQUESTER = auto()
    RESPONDER = auto()
    UNKNOWN = auto()


class PromptTTL(Enum):
    MULTI_TURN = auto()  # プロンプト生成で複数ターンぶんのプロンプトを生成する
    SINGLE_TURN = auto()  # プロンプト生成で１ターンぶん（一問一答）のプロンプトを生成する


class ChatContent:
    def __init__(self, role: str, msg: str = "", msg_id: str = None, role_type: RoleType = RoleType.UNKNOWN, child_msgs=None):
        self.role = role
        self.role_type = role_type
        self.message = msg
        self.message_id = msg_id
        self.child_messages = child_msgs

    def get_role_type(self):
        return self.role_type

    def get_role(self):
        return self.role

    def get_message(self):
        return self.message

    def set_message_id(self, message_id: str):
        """
        メッセージIDをセットする
        :return:
        """
        self.message_id = message_id

    def get_message_id(self):
        """
        メッセージIDを取得する
        :return:
        """
        return self.message_id

    def set_message(self, msg: str):
        """
        メッセージをセットする
        :param msg:
        :return:
        """
        self.message = msg

    def add_child_message(self, msg: str):
        if not self.child_messages:
            self.child_messages = []
        self.child_messages.append(msg)

    def get_child_messages(self):
        return self.child_messages

    def has_child_messages(self):
        """
        Checks if there are any child messages.

        :return: True if child messages exist and contain at least one element, otherwise False.
        """
        return self.child_messages is not None and len(self.child_messages) > 0

    def to_dict(self):
        return {
            "role": self.role,
            "role_type": self.role_type.name,  # Enum value to string conversion
            "message": self.message,
            "message_id": self.message_id,
            "child_messages": self.child_messages
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            role=data["role"],
            msg=data["message"],
            msg_id=data["message_id"],
            role_type=RoleType[data["role_type"]],  # Convert string back to Enum value
            child_msgs=data["child_messages"] if "child_messages" in data else None
        )


class AbstractChatPrompt(ABC):
    """
    A builder to build chat prompts according to the characteristics of each language model.
    """

    def __init__(self):
        self.system = ""
        self.chat_contents = []
        self.responder_messages = []
        self.requester_messages = []
        self.requester = ""
        self.responder = ""
        self.chat_mode = True
        self.special_tokens = None
        # [prefix_as_stop_str_enabled]
        # True:文章生成で EOS での停止が不安定なモデルの場合に
        # 応答側メッセージの接頭辞「<bot>」などを停止文字列として使用する
        # get_stop_strs に直接指定することも可能
        self.prefix_as_stop_str_enabled = False
        self.responder_prefix_as_stop_str = None
        self.final_stop_strs = None  # 停止文字列（群）の確定版
        self.prompt_ttl_mode = PromptTTL.MULTI_TURN

    def clear_history(self):
        self.chat_contents = []
        self.responder_messages = []
        self.requester_messages = []

    def set_prompt_ttl(self, prompt_ttl):
        """
        Set whether single-turn or multi-turn when generating prompts. Default is multi-turn

        :param prompt_ttl:
        PromptTTL.SINGLE_TURN: Clear prompts per turn and do not use history
        PromptTTL.MULTI_TURN:  Create prompts from all previous conversation history
        """

        # マルチターンプロンプトかシングルターンプロンプトかをセットする
        self.prompt_ttl_mode = prompt_ttl

    def set_tokenizer(self, tokenizer):
        # special_token を取得するためにトークナイザーをセットする

        # 特殊トークンを取得
        if tokenizer is not None:
            self.special_tokens = tokenizer.special_tokens_map.values()

    def get_contents(self, opts={}):
        """
        これまでの会話履歴(list)を取得する
        :param opts:
        "omit_last_message":True の場合、最新のメッセージは会話履歴に含めないで返す
        "to_message_id": ここにメッセージID を指定すると、そのメッセージIDまでの会話履歴を返す
        :return:
        """

        omit_last_message = opts.get("omit_last_message", False)
        to_message_id = opts.get("to_message_id", None)

        list = []
        for idx, chat_content in enumerate(self.chat_contents):
            is_last = (idx == len(self.chat_contents) - 1)

            if omit_last_message and is_last:
                chat_content_role = chat_content.get_role()
                # chat_content_message = chat_content.get_message()
                last_content = ChatContent(role=chat_content_role, msg=None)
                list.append(last_content)
            else:
                list.append(chat_content)

            if to_message_id is not None:
                message_id = chat_content.get_message_id()
                if to_message_id == message_id:
                    return list  # to_message_id が検出されたらそこで出力終了

        if self.prompt_ttl_mode == PromptTTL.SINGLE_TURN:
            if len(list) >= 2:
                list = list[-2:]

        return list

    def find_chat_content_by_message_id(self, message_id):
        """
        メッセージIDで chat_content を検索する
        :param message_id:
        :return:
        """
        for idx, chat_content in enumerate(self.chat_contents):
            if chat_content.get_message_id() is not None and chat_content.get_message_id() == message_id:
                return chat_content
        return None

    def get_turn(self):
        """
        現在のターン数を返す
        往復で１ターンと数える
        :return:
        """
        return len(self.requester_messages)

    def set_chat_mode_enabled(self, enabled):
        self.chat_mode = enabled

    def is_chat_mode_enabled(self):
        return self.chat_mode

    def set_system(self, system):
        """
        Set initial prompts for "system."
        :param system:
        :return:
        """
        self.system = system

    def set_requester(self, requester):
        """
        Sets the role name of the requester (=user)
        :param requester:
        :return:
        """
        self.requester = requester

    def set_responder(self, responder):
        """
        Sets the role name of the responder (=AI)
        :param responder:
        :return:
        """
        self.responder = responder

    def set_prefix_as_stop_str_enabled(self, enabled):
        """
        For models with unstable stopping at EOS in sentence generation.
        Use the prefix of the response side message
         (e.g., "<bot>" or "system:", which is generated as the response side prefix, as the stop string.)
        Can also be specified directly in get_stop_strs
        :param enabled:
        :return:
        """
        self.prefix_as_stop_str_enabled = enabled

        if enabled:
            self.clear_history()  # プロンプト履歴無し状態で実行する必要があるため履歴をクリア
            pre_prompt = self.create_prompt()
            self.add_requester_msg(None)
            prompt = self.create_prompt()

            # promptがpre_promptから始まる場合、pre_promptの長さ分だけ削除
            requester_prefix = prompt
            if prompt.startswith(pre_prompt):
                requester_prefix = prompt[len(pre_prompt):]

            # responderの接頭辞を停止文字列として使用する設定が有効なとき
            if requester_prefix is None or requester_prefix == "":
                raise ValueError(
                    "Prompt cannot be None or an empty string."
                    "Before calling this method, specify set_responder and set_requester to ensure that the prompt is built correctly with create_prompt.")

            self.responder_prefix_as_stop_str = requester_prefix

            self.clear_history()  # 今、responder_prefix_as_stop_str生成のために履歴を作ったため元にもどすため履歴をクリア

    def add_requester_msg(self, message, child_message=None, child_messages=None):
        """
        Adds a requester's message.

        :param message: The main content of the message (str).
        :param child_message: A single child message (str). Cannot be specified together with child_messages.
        :param child_messages: An array of child messages (list of str). Must contain at least one element.
        :raises ValueError: If both child_message and child_messages are specified, or if the format of child_messages is incorrect.
        """

        if child_message is not None and child_messages is not None:
            raise ValueError("You cannot specify both child_message and child_messages. Please specify only one of them.")

        if child_message is not None:
            child_msgs = [child_message]
        elif child_messages is not None:
            if isinstance(child_messages, list) and all(isinstance(item, str) for item in child_messages) and len(child_messages) > 0:
                child_msgs = child_messages
            else:
                raise ValueError("child_messages must be an array of strings with at least one element.")
        else:
            child_msgs = None

        self._add_msg(ChatContent(role=self.requester, msg=message, role_type=RoleType.REQUESTER, child_msgs=child_msgs))

    def add_responder_msg(self, message):
        self._add_msg(ChatContent(role=self.responder, msg=message, role_type=RoleType.RESPONDER))

    def get_responder_last_msg(self):
        """
        AI側の最新メッセージを取得する
        """
        return self.responder_messages[-1].message if self.responder_messages else None

    def get_requester_last_msg(self):
        """
        ユーザーからの最新メッセージを取得する
        """
        # ユーザーメッセージがあれば最新のものを、なければNoneを返す
        return self.requester_messages[-1].message if self.requester_messages else None

    def clear_last_responder_message(self):
        """
        Set the message of the last response from the responder (AI) to None.
        """
        if self.responder_messages and self.chat_contents and self.chat_contents[-1].get_role() == self.responder:
            # 最後のメッセージが応答者（AIアシスタント側）の場合
            self.responder_messages[-1].set_message(None)
            self.chat_contents[-1].set_message(None)
        else:
            pass

    def remove_last_requester_msg(self):
        """
        ユーザー側の最新メッセージを削除
        """
        last_chat_content = self.chat_contents[-1]
        last_chat_content_role = last_chat_content.get_role()

        if last_chat_content_role == self.responder:
            raise ValueError("Last chat content role must be requester")

        if self.chat_contents:
            if self.requester_messages and last_chat_content_role == self.requester:
                self.requester_messages.pop()
                self.chat_contents.pop()

    def remove_last_responder_msg(self):
        """
        AI側の最新メッセージを削除
        """
        last_chat_content = self.chat_contents[-1]
        last_chat_content_role = last_chat_content.get_role()

        if last_chat_content_role != self.responder:
            raise ValueError("Last chat content role must be responder")

        if self.responder_messages and self.chat_contents:
            self.responder_messages.pop()
            self.chat_contents.pop()

    def set_responder_last_msg(self, message):
        """
        AI 側の最新メッセージを更新する
        """

        # responder_messagesリストの最後のメッセージを更新
        self.responder_messages[-1].message = message
        self.chat_contents[-1].set_message(message)

    def set_responder_last_msg_id(self, message_id):
        """
        AI 側の最新メッセージのメッセージIDを設定する
        """

        # responder_messagesリストの最後のメッセージを更新
        self.responder_messages[-1].set_message_id(message_id)

        # self.chat_contents[-1].set_message_id(message_id)
        for chat_content in reversed(self.chat_contents):
            if chat_content.get_role_type() == RoleType.RESPONDER:
                chat_content.set_message_id(message_id)
                break

    def _add_msg(self, chat_content_obj):
        # チャットメッセージリストに追加
        self.chat_contents.append(chat_content_obj)
        if chat_content_obj.role_type == RoleType.RESPONDER:
            self.responder_messages.append(chat_content_obj)
        elif chat_content_obj.role_type == RoleType.REQUESTER:
            # If necessary, replace line breaks, etc. in the input string with tokens understood by the tokenizer.
            # ユーザーによる入力を置換指定された条件で置換する

            requester_message_text = chat_content_obj.get_message()

            final_msg_str = requester_message_text
            if self.get_replacement_when_input() is not None:
                if requester_message_text is not None:
                    final_msg_str = self.replace_string(requester_message_text, self.get_replacement_when_input())

            chat_content_obj.set_message(final_msg_str)
            # requester メッセージリストに追加
            self.requester_messages.append(chat_content_obj)

    def is_requester_role(self, role):
        if self.requester == role:
            return True
        else:
            return False

    def get_skip_len(self, omit_last_message=False):
        """
        （Get the length to skip (already entered as a prompt)
        :return:
        """
        current_prompt = self.create_prompt({"omit_last_message": omit_last_message})

        # skip_special_tokens = True なので、スキップすべき長さは special_tokens を含まない長さとなるので
        # 長さを計測する用の現在のプロンプトから special_tokens を削除する
        if self.special_tokens is not None:
            # 特殊トークンを削除
            for token in self.special_tokens:
                if isinstance(token, str):
                    # 特殊トークンが str 型のとき
                    current_prompt = current_prompt.replace(token, '')
                elif isinstance(token, list):
                    # 特殊トークンが list 型のとき
                    # 例)LlamaTokenizer.from_pretrained("novelai/nerdstash-tokenizer-v1", additional_special_tokens=['▁▁']) のように指定してあるときなど
                    for sub_token in token:
                        if isinstance(sub_token, str):
                            current_prompt = current_prompt.replace(sub_token, '')

        skip_echo_len = len(current_prompt)

        # モデルからの出力と、入力プロンプトの不整合が起こるモデルがあるため、
        # 出力プロンプトから入力プロンプトを引き算するときの　入力プロンプトの長さ　をモディファイできる
        # get_custom_skip_echo_len を実行する
        # https://github.com/qualiteg/ChatStream/issues/23
        skip_echo_len = self.get_custom_skip_echo_len(skip_echo_len)

        return skip_echo_len

    def is_empty(self):
        """
        チャットプロンプトが空かどうかを確認する
        """
        return not self.requester_messages and not self.responder_messages

    def replace_string(self, original_string, replace_list):
        """
        original_string を replace_list にある置換ペア（タプル）にしたがって置換する
        replace_list =[("A","B"),("C","D")] の場合、
        original_string にある "A" は "B" に置換される。 "C" は "D" に置換される。
        replace A with B and replace C with D
        """
        if replace_list is None:
            return original_string
        for old, new in replace_list:
            original_string = original_string.replace(old, new)
        return original_string

    def to_dict(self):
        """
        シリアライズ
        データベースやファイルに保存用に。
        """
        return {
            "system": self.system,
            "chat_contents": [chat_content.to_dict() for chat_content in self.chat_contents],
            "responder_messages": [responder_message.to_dict() for responder_message in self.responder_messages],
            "requester_messages": [requester_message.to_dict() for requester_message in self.requester_messages],
            "requester": self.requester,
            "responder": self.responder,
            "chat_mode": self.chat_mode,
        }

    @classmethod
    def from_dict(cls, data):
        """
        デシリアライズ
        データベース、ファイルからの復元
        """
        chat_prompt = cls()
        chat_prompt.system = data["system"]
        chat_prompt.chat_contents = [ChatContent.from_dict(chat_content_data) for chat_content_data in data["chat_contents"]]
        chat_prompt.responder_messages = [ChatContent.from_dict(responder_message_data) for responder_message_data in data["responder_messages"]]
        chat_prompt.requester_messages = [ChatContent.from_dict(requester_message_data) for requester_message_data in data["requester_messages"]]
        chat_prompt.requester = data["requester"]
        chat_prompt.responder = data["responder"]
        chat_prompt.chat_mode = data["chat_mode"]
        return chat_prompt

    def _get_final_stop_strs(self):
        """
        Retrieves the final stop strings by combining two sources:
        1. Stop strings that are obtained from the get_stop_strs method.
        2. If prefix_as_stop_str_enabled is set to True (by calling set_prefix_as_stop_str_enabled)
            and responder_prefix_as_stop_str is specified,
           then the prefix of the responder is also added as a stop string.

        The combination of these two sources forms the final stop strings,
        which are then returned.

        :return: A list of final stop strings, combined from both sources as described above.
        """
        if not self.final_stop_strs:
            self.final_stop_strs = []
            if self.prefix_as_stop_str_enabled and self.responder_prefix_as_stop_str:
                # responder の 接頭辞を停止文字列として使用する設定が有効なとき
                self.final_stop_strs.append(self.responder_prefix_as_stop_str)

            stop_strs_from_method = self.get_stop_strs()

            if isinstance(stop_strs_from_method, list):
                self.final_stop_strs += stop_strs_from_method

        return self.final_stop_strs

    def get_stop_strs(self):
        """
        Override this method when you want to manually specify stop strings.

        If you want to use the requester's prefix as a stop string, it is
        recommended to call the set_prefix_as_stop_str_enabled method instead
        of overriding this method.

        :return: None by default. Should return a list of stop strings like ["\n\n","\n<"]  if overridden.
        """

        # 停止文字列を使用したい場合は具象クラス側でオーバーライドしてリスト型で列挙する
        # 例) return ["\n\n","\n<"]
        return None

    @abstractmethod
    def create_prompt(self, opts):
        pass

    @abstractmethod
    def build_initial_prompt(self, chat_prompt_obj):
        """
        初期プロンプトを生成する
        """

        # オーバーライドして初期プロンプトの生成コードを（必要があれば）記述する
        pass

    def get_replacement_when_input(self):
        """
        ユーザーからの入力文字列を指定した置換ルールにしたがって置換する
        """
        return None

    def get_replacement_when_output(self):
        """
        モデルからの逐次出力トークンを置換ルールにしたがって置換する
        """
        return None

    def get_custom_skip_echo_len(self, skip_echo_len):
        """
        skip_echo_len をモデルに応じてモディファイする
        skip_echo_len は 現在の入力プロンプトの長さを示す
        この長さは、新しく
        """
        return skip_echo_len
