from chatstream import AbstractChatPrompt


class ChatPromptStockmarkGptNeoxJp(AbstractChatPrompt):
    """
    https://huggingface.co/stockmark/gpt-neox-japanese-1.4b
    """

    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_requester("")
        self.set_responder("")

    def get_stop_strs(self):
        if not self.chat_mode:
            return None
        return []

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

            if chat_content_message:
                merged_message = chat_content_message

            ret += merged_message

        return ret

    def build_initial_prompt(self, chat_prompt):
        # 初期プロンプトは実装しない
        pass


# portable UT
if True:
    chat_prompt = ChatPromptStockmarkGptNeoxJp()

    chat_prompt.add_requester_msg("AIによって私達の暮らしは、")
    chat_prompt.add_responder_msg("豊かになった")

    # print(f"{chat_prompt.create_prompt()}")
    assert """AIによって私達の暮らしは、豊かになった""" == chat_prompt.create_prompt()
