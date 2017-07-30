
from commands import command
from TelegramUser import UserFinder

def find_user(user, message, command_info, **kwars):
    if "Admin" not in user.privileges:
        user.sendMessage("Only admins can find users.")
        return
    if len(message) != 2:
        user.sendMessage(command_info.help_use_hint)
        return
    found = UserFinder.get_user_by_username(message[1])
    if not found:
        user.sendMessage("User not found")
        return
    user.sendMessage(str(found))


command("/finduser", find_user, help_description="Finds an user by username",
        help_use_hint="Write the user name after the command, /finduser someone")



def me(user, **kwars):
    user.sendMessage(str(user))


command("/Me", me, help_description="Shows your own information")