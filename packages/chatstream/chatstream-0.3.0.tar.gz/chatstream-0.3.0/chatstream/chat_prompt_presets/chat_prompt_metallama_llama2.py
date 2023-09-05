from chatstream import AbstractChatPrompt
from chatstream.chat_prompt import RoleType

SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\
"""


class ChatPromptMetaLlamaLlama2Chat(AbstractChatPrompt):
    """
    meta-llama/Llama-2-7b-chat

    Prompt Guide from
    https://huggingface.co/blog/llama2
    """

    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_system(f"<s>[INST] <<SYS>>\n{SYSTEM_PROMPT}\n<</SYS>>\n\n")
        self.set_requester("")
        self.set_responder("")

    def get_stop_strs(self):
        if not self.chat_mode:
            return None
        return []

    def get_custom_skip_echo_len(self, skip_echo_len):
        # modify skip_echo_len when using llama2
        # details on https://github.com/qualiteg/ChatStream/issues/23
        num_turn = self.get_turn()
        if num_turn >= 2:
            modified_skip_echo_len = skip_echo_len + 1 * self.get_turn()
            return modified_skip_echo_len
        return skip_echo_len

    def get_replacement_when_input(self):
        return None

    def get_replacement_when_output(self):  # replace when response_text gotten
        return None

    def create_prompt(self, opts={}):
        if self.chat_mode == False:
            return self.get_requester_last_msg()

        # Chat Mode == True の場合のプロンプトを構築する
        ret = self.system

        for chat_content in self.get_contents(opts):

            chat_content_role_type = chat_content.get_role_type()
            chat_content_message = chat_content.get_message()

            if chat_content_message:
                if chat_content_role_type is RoleType.REQUESTER:
                    merged_message = f"{chat_content_message} [/INST] "
                elif chat_content_role_type is RoleType.RESPONDER:
                    merged_message = f"{chat_content_message} </s><s>[INST] "
                ret += merged_message
            else:
                pass

        return ret

    def build_initial_prompt(self, chat_prompt):
        # 初期プロンプトは実装しない
        pass


# portable UT
if False:
    chat_prompt = ChatPromptLlama2()

    chat_prompt.add_requester_msg("What spots do you recommend that I should go sightseeing in Tokyo?")
    chat_prompt.add_responder_msg("I recommend Sensoji Temple and Tokyo Tower in Asakusa.")
    chat_prompt.add_requester_msg("Are there any good restaurants nearby?")

    # print(f"{chat_prompt.create_prompt()}")
    assert """<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

What spots do you recommend that I should go sightseeing in Tokyo? [/INST] I recommend Sensoji Temple and Tokyo Tower in Asakusa. </s><s>[INST] Are there any good restaurants nearby? [/INST] """ == chat_prompt.create_prompt()
