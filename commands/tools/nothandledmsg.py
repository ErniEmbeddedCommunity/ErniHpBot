from commands import PatternCommand, HandledStatus


@PatternCommand.register("(.*)", execution_preference=-10)
def not_handled_msg(chat, message, handled,  **kwargs):
    if handled is HandledStatus.NOT_HANDLED:
        chat.sendMessage("I don't know what you mean with " +
                         str(message[0]) + "\nTry /help")
