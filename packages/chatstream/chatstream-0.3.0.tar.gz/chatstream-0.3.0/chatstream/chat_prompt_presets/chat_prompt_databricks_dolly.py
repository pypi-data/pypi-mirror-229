from chatstream import AbstractChatPrompt
from chatstream.chat_prompt import PromptTTL


class ChatPromptDatabricksDolly(AbstractChatPrompt):
    """
    ChatPrompt implementation supporting the following LLMs

    - databricks/dolly-v2-3b (https://huggingface.co/databricks/dolly-v2-3b)
    - databricks/dolly-v2-7b (https://huggingface.co/databricks/dolly-v2-7b)
    """

    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_system("Below is an instruction that describes a task. Write a response that appropriately completes the request.")
        self.set_requester("Instruction")
        self.set_responder("Response")
        self.set_prefix_as_stop_str_enabled(True)  # enable requester's prompt suffix as stop str
        self.set_prompt_ttl(PromptTTL.MULTI_TURN)

    def get_replacement_when_input(self):
        return None

    def get_replacement_when_output(self):
        return None

    def create_prompt(self, opts={}):
        if not self.chat_mode:
            return self.get_requester_last_msg()

        ret = self.system + "\n\n";
        for chat_content in self.get_contents(opts):

            chat_content_role = chat_content.get_role()
            chat_content_message = chat_content.get_message()

            if chat_content_role:

                if chat_content_message:
                    merged_message = f"### {chat_content_role}:\n" + chat_content_message + "\n\n"
                else:
                    merged_message = f"### {chat_content_role}:\n"

                ret += merged_message

        return ret

    def build_initial_prompt(self, chat_prompt):
        pass
