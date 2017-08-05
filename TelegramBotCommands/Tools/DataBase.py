
from ..CommandsBase import BaseCommand, PatternCommand, HandledStatus, ChatType, KeyboardCommand

KEYBOARD = KeyboardCommand() 

@BaseCommand.register("/dbreset",
                      help_description="Removes all the user data from the database.",
                      available_in=set({ChatType.PRIVATE}))
def reset(chat, **kwargs):
    KEYBOARD.send(chat, "¿Are you sure?",["Yes","No"], get_confirmation)


def get_confirmation(chat, user, key, **kwargs):
    # confirmation_command.enabled = False
    if key == "yes":
        chat.sendMessage("Reset complete, send /start to complete reboot")
        user.remove_all_data_from_database()
    if key == "no":
        chat.sendMessage("Cancellded")
    if key == None:
        # sends the keyboard again
        KEYBOARD.send(chat, "Please, use the keyboard",["Yes","No"], get_confirmation)
    # makes sure that any other command catchs the message by error
    return HandledStatus.HANDLED_BREAK


