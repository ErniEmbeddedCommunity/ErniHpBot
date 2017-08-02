
from commands import command, ChatType
from TelegramUser import TUser


def init_database(user, **kwargs):
    """Creates the key in the database for privileges"""
    privileges = user.privileges
    if privileges == None:
        user.privileges = set()


command("/start", init_database)


def give_access(user, chat, message, command_info, **kwargs):
    if "Admin" not in user.privileges:
        chat.sendMessage("Only admins can give access.")
        return
    if len(message) != 3:
        chat.sendMessage(command_info.help_use_hint)
        return
    target_username = message[1]
    privilege = message[2]
    target = TUser.get_user_by_username(target_username)
    if not target:
        chat.sendMessage("User " + target_username + " do not exist")
        return
    target.privileges.add(privilege)
    chat.sendMessage(target_username + " is " + privilege + " now.")

    target.sendMessage(user.username + " gives your right to " + privilege)


def remove_access(user, chat, message, command_info, **kwargs):
    if "Admin" not in user.privileges:
        chat.sendMessage("Only admins can remove access.")
        return
    if len(message) != 3:
        chat.sendMessage(command_info.help_use_hint)
        return
    target_username = message[1]
    privilege = message[2]
    target = TUser.get_user_by_username(target_username)
    if not target:
        chat.sendMessage("User " + target_username + " do not exist")
        return
    if message[2] == "Admin" and user == target:
        chat.sendMessage("You can't remove Admin rights from yourself")
        return
    target.privileges.remove(privilege)
    chat.sendMessage(target_username + " is no longer " + privilege)
    target.sendMessage(user.username + " removes your right to " + privilege)


def check_access(user, chat, **kwargs):
    chat.sendMessage(str(user.privileges))


command("/GiveAccess", give_access,
        help_description="Give Access to user",
        help_use_hint="Usage: /GiveAccess @username Led")
command("/RemoveAccess", remove_access,
        help_description="Remove Access to user,",
        help_use_hint="Usage: /RemoveAccess @username Led")
command("/CheckAccess", check_access,
        help_description="Check things that you or other user have access to.")


def set_admin(user, **kwargs):
    user.privileges.add("Admin")
    user.sendMessage("You are Admin now")


command("/Admin", set_admin, help_description="CHEAT!, gives you Admin rights",
        available_in=set({ChatType.PRIVATE}))
