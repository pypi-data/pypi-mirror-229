from chatstream.chat_prompt import AbstractChatPrompt


class ChatPromptTogetherRedPajamaINCITEChat(AbstractChatPrompt):
    """
    togethercomputer/RedPajama-INCITE-7B-Chat
    """
    def __init__(self):
        super().__init__()  # Call the initialization of the base class
        self.set_requester("<human>")
        self.set_responder("<bot>")
        self.set_prefix_as_stop_str_enabled(True)  # enable requester's prompt suffix as stop str

    def get_stop_strs(self):
        return ['<|endoftext|>']

    def create_prompt(self, opts={}):
        """
        Build prompts according to the characteristics of each language model
        :return:
        """
        if self.chat_mode == False:
            return self.get_requester_last_msg()

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
        pass
        # If you want a common initial prompt for instructions, override this method and implement
        # chat_prompt.add_requester_msg("Do you know about the Titanic movie?")
        # chat_prompt.add_responder_msg("Yes, I am familiar with it.")
        # chat_prompt.add_requester_msg("Who starred in the movie?")
        # chat_prompt.add_responder_msg("Leonardo DiCaprio and Kate Winslet.")


# portable UT
if False:
    chat_prompt = ChatPromptTogetherRedPajamaINCITEChat()

    chat_prompt.set_requester("<human>")
    chat_prompt.set_responder("<bot>")
    chat_prompt.add_requester_msg("Who is Alan Turing")
    chat_prompt.add_responder_msg(None)

    # print(f"{chat_prompt.create_prompt()}")
    assert """<human>: Who is Alan Turing
<bot>:""" == chat_prompt.create_prompt()

    assert "<human>:" == chat_prompt._get_final_stop_strs()[0]
