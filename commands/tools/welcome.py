
from commands import BaseCommand, HandledStatus


@BaseCommand.register("/start",
        help_description="Initialize modules", execution_preference=-1)
def say_hello(chat, **kargs):
    chat.sendMessage("Welcome, Try /help")
