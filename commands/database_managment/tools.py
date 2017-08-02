
import re
import redis
from commands import command, pattern_command, HandledStatus, ChatType,KeyboardCommand


def reset(chat, **kwargs):
    keyboard.send(chat)
    # chat.sendMessage("¿Are you sure?", ["Yes", "No"])
    # confirmation_command.enabled = True


def get_confirmation(chat, user, key, **kwargs):
    # confirmation_command.enabled = False
    if key == "yes":
        chat.sendMessage("Reset complete, send /start to complete reboot")
        user.remove_all_data_from_database()
    if key == "no":
        chat.sendMessage("Cancellded")
    if key == None:
        # sends the keyboard again
        keyboard.send(chat,"Please, use the keyboard")
    # makes sure that any other command catchs the message by error
    return HandledStatus.HANDLED_BREAK

command("/dbreset", reset, help_description="Removes all the user data from the database.",
        available_in=set({ChatType.PRIVATE}))
# confirmation_command = pattern_command(
#     "(.*)", get_confirmation, enabled=False, execution_preference=5)
keyboard = KeyboardCommand(["yes","no"],get_confirmation,"¿Are you sure?")