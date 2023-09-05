from chatstream import AbstractChatPrompt


class ChatPromptOpenlmrOpenLlama(AbstractChatPrompt):
    """
    Q&A scene prompt for openlm-research/open_llama_3b_v2
    """

    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_requester("Q")
        self.set_responder("A")

    def get_stop_strs(self):
        if not self.chat_mode:
            return None
        return ["\nQ:", "\nB:", "\nC:"]  # https://github.com/qualiteg/ChatStream/issues/26

    def get_replacement_when_input(self):
        return None

    def get_replacement_when_output(self):
        return None

    def create_prompt(self, opts=None):
        if opts is None:
            opts = {}

        if self.chat_mode == False:
            return self.get_requester_last_msg()

        # Chat Mode == True の場合のプロンプトを構築する
        ret = self.system
        for chat_content in self.get_contents(opts):
            chat_content_role = chat_content.get_role()
            chat_content_message = chat_content.get_message()
            if chat_content_role:
                if chat_content_message:
                    merged_message = chat_content_role + ": " + chat_content_message + "\n"
                else:
                    merged_message = chat_content_role + ":"
                ret += merged_message

        return ret

    def build_initial_prompt(self, chat_prompt):
        # 初期プロンプトは実装しない
        pass


# portable UT
if False:
    chat_prompt = ChatPromptOpenLlama()

    chat_prompt.add_requester_msg("What is the largest animal?")
    chat_prompt.add_responder_msg("The largest animal is elephant.")

    print(f"'{chat_prompt.create_prompt()}'")
    assert """Q: What is the largest animal?\nA: The largest animal is elephant.\n""" == chat_prompt.create_prompt()
