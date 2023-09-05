from chatstream import AbstractChatPrompt
from chatstream.chat_prompt import RoleType, PromptTTL


class ChatPromptLineCorpJpLargeLmInstSft(AbstractChatPrompt):
    """
    ChatPrompt implementation supporting the following LLMs

    - line-corporation/japanese-large-lm-3.6b-instruction-sft
    (https://huggingface.co/line-corporation/japanese-large-lm-3.6b-instruction-sft)

    """

    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_requester("ユーザー")
        self.set_responder("システム")
        self.set_prefix_as_stop_str_enabled(True)  # enable requester's prompt suffix as stop str
        self.set_prompt_ttl(PromptTTL.MULTI_TURN)

    def get_stop_strs(self):
        return None

    def get_replacement_when_input(self):
        return None

    def get_replacement_when_output(self):
        return None

    def create_prompt(self, opts={}):
        if self.chat_mode == False:
            return self.get_requester_last_msg()

        ret = self.system;
        for chat_content in self.get_contents(opts):

            chat_content_role = chat_content.get_role()
            chat_content_role_type = chat_content.get_role_type()
            chat_content_message = chat_content.get_message()

            if chat_content_role:

                if chat_content_message:

                    merged_message = chat_content_role + ": " + chat_content_message

                    if chat_content_role_type == RoleType.REQUESTER:
                        merged_message += "\n"
                else:
                    merged_message = chat_content_role + ": "

                ret += merged_message

        return ret

    def build_initial_prompt(self, chat_prompt):
        # 初期プロンプトは実装しない
        pass


# portable UT
if False:
    chat_prompt = ChatPromptLineCorpJpLargeInstSft()

    chat_prompt.add_requester_msg("四国の県名を全て列挙してください。")
    chat_prompt.add_responder_msg("高知県、徳島県、香川県、愛媛県")

    print(f"{chat_prompt.create_prompt()}")

    assert "ユーザー: 四国の県名を全て列挙してください。\nシステム: 高知県、徳島県、香川県、愛媛県" == chat_prompt.create_prompt()
