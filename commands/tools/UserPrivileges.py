
from commands import command
from TelegramUser import UserFinder


def init_database(user, **kwargs):
    """Creates the key in the database for privileges"""
    privileges = user.privileges
    if privileges == None:
        user.privileges = set()



command("/start", init_database)

def give_access(user, message, command_info, **kwargs):
    if "Admin" not in user.privileges:
        user.sendMessage("Only admins can give access.")
        return
    if len(message) != 3:
        user.sendMessage(command_info.help_use_hint)
        return
    target_username = message[1]
    privilege = message[2]
    target = UserFinder.get_user_by_username(target_username)
    if not target:
        user.sendMessage("User " + target_username + " do not exist")
        return
    target.privileges.add(privilege)
    user.sendMessage(target_username + " is " + privilege + " now.")

    target.sendMessage(user.username + " gives your right to " + privilege)


def remove_access(user, message, command_info, **kwargs):
    if "Admin" not in user.privileges:
        user.sendMessage("Only admins can remove access.")
        return
    if len(message) != 3:
        user.sendMessage(command_info.help_use_hint)
        return
    target_username = message[1]
    privilege = message[2]
    target = UserFinder.get_user_by_username(target_username)
    if not target:
        user.sendMessage("User " + target_username + " do not exist")
        return
    if message[2] == "Admin" and user == target:
        user.sendMessage("You can't remove Admin rights from yourself")
        return
    target.privileges.remove(privilege)
    user.sendMessage(target_username + " is no longer " + privilege)
    target.sendMessage(user.username + " removes your right to " + privilege)


def check_access(user, **kwargs):
    user.sendMessage(str(user.privileges))


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

command("/Admin", set_admin, help_description="CHEAT!, gives you Admin rights")
