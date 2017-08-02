
from commands import command
from TelegramUser import TUser

def find_user(user, chat, message, command_info, **kwars):
    if "Admin" not in user.privileges:
        chat.sendMessage("Only admins can find users.")
        return
    if len(message) != 2:
        chat.sendMessage(command_info.help_use_hint)
        return
    found = TUser.get_user_by_username(message[1])
    if not found:
        chat.sendMessage("User not found")
        return
    chat.sendMessage(str(found))


command("/finduser", find_user, help_description="Finds an user by username",
        help_use_hint="Write the user name after the command, /finduser someone")



def me(user, chat,  **kwars):
    chat.sendMessage(str(user))


command("/Me", me, help_description="Shows your own information")