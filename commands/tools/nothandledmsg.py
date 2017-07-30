from commands import pattern_command, HandledStatus


def not_handled_msg(user, message, handled,  **kwargs):
    if handled is HandledStatus.NOT_HANDLED:
        user.sendMessage("I don't know what you mean with " + str(message[0]) + "\nTry /help")


pattern_command("(.*)", not_handled_msg , execution_preference=-10)