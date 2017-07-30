from commands import command, pattern_command, HandledStatus

import re
import redis

confirm = False


def reset(user, **kwargs):
    global confirm
    if not confirm:
        confirm = True
        user.sendMessage("¿Are you sure?")
    else:
        confirm = False
        user.sendMessage("Reset complete, send /start to complete reboot")
        user.remove_all_data_from_database()

def monitor(**kwargs):
    global confirm
    confirm = False
    return HandledStatus.NOT_HANDLED

command("/dbreset",reset, help_description="Removes all the user data from the database.")
pattern_command("^/(?!dbreset)", monitor)