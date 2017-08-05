
from ..CommandsBase import BaseCommand
from ..TelegramUser import TUser
# from UserPrivileges import check_for_access


@BaseCommand.register("/finduser",
                      help_description="Finds an user by username",
                      help_use_hint="Write the user name after the command, /finduser someone")
def find_user(user, chat, message, command_info, **kwars):
    # if check_for_access(user, command_info):
    #     chat.sendMessage("Only admins can find users.")
    #     return
    if len(message) != 2:
        chat.sendMessage(command_info.help_use_hint)
        return
    found = TUser.get_user_by_username(message[1])
    if not found:
        chat.sendMessage("User not found")
        return
    chat.sendMessage(str(found))


@BaseCommand.register("/Me",
                      help_description="Shows your own information")
def me(user, chat,  **kwars):
    chat.sendMessage(str(user))
