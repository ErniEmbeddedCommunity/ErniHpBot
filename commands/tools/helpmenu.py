from commands import BaseCommand
import commands.CommandsBase as CommandsBase



@BaseCommand.register("/help", help_description="Prints this message.")
def show_help(user, chat, **kwargs):
    allcommands = list(CommandsBase._registered_commands)
    helplist = [command for command in allcommands if command.help_description != "" ]
    helpstrings = list(map(str,helplist))
    # helpstrings.sort()
    helplines = "\n\n".join(helpstrings)
    chat.sendMessage(helplines)

