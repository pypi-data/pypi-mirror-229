from chatstream import AbstractChatPrompt
from chatstream.chat_prompt import PromptTTL


class ChatPromptStabilityAiJpGptNeoxInstSft(AbstractChatPrompt):
    """
    https://huggingface.co/rinna/japanese-gpt-neox-3.6b-instruction-sft
    """

    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_system("以下は、タスクを説明する指示と、文脈のある入力の組み合わせです。要求を適切に満たす応答を書きなさい。")
        self.set_requester("指示")
        self.set_responder("応答")
        self.set_prefix_as_stop_str_enabled(True)  # enable requester's prompt suffix as stop str
        self.set_prompt_ttl(PromptTTL.MULTI_TURN) # SINGLE_TURN:Clear prompts per turn and do not use history

    # def get_stop_strs(self):
    #     if not self.chat_mode:
    #         return None
    #     return ["### 指示:"]

    def get_replacement_when_input(self):
        return None

    def get_replacement_when_output(self):
        return None

    def create_prompt(self, opts={}):
        if self.chat_mode == False:
            return self.get_requester_last_msg()

        # Chat Mode == True の場合のプロンプトを構築する
        ret = self.system + "\n\n";
        for chat_content in self.get_contents(opts):

            chat_content_role = chat_content.get_role()
            chat_content_message = chat_content.get_message()
            chat_content_child_messages = chat_content.get_child_messages()
            has_child_messages = chat_content.has_child_messages()

            if chat_content_role:

                if chat_content_message:
                    merged_message = f"### {chat_content_role}: \n" + chat_content_message + "\n\n"
                    if has_child_messages:
                        merged_message += f"### 入力: \n"
                        chat_content_child_messages = chat_content.get_child_messages()
                        for message in chat_content_child_messages:
                            merged_message += message + "\n\n"
                else:
                    merged_message = f"### {chat_content_role}: "

                ret += merged_message

        return ret

    def build_initial_prompt(self, chat_prompt):
        # 初期プロンプトは実装しない
        pass


# portable UT
if False:
    chat_prompt = ChatPromptStabilityAiJapaneseStablelmInstruct()
    chat_prompt.set_system("以下は、タスクを説明する指示と、文脈のある入力の組み合わせです。要求を適切に満たす応答を書きなさい。")
    chat_prompt.add_requester_msg("VR について、以下の比較対象との違いを箇条書きで教えてください。", child_message="比較対象: AR")
    chat_prompt.add_responder_msg(None)

    expected = "以下は、タスクを説明する指示と、文脈のある入力の組み合わせです。要求を適切に満たす応答を書きなさい。\n\n### 指示: \nVR について、以下の比較対象との違いを箇条書きで教えてください。\n\n### 入力: \n比較対象: AR\n\n### 応答: "
    prompt = chat_prompt.create_prompt()
    assert expected == prompt

    print(prompt)
