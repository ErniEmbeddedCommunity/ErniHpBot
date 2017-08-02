
from commands import command, HandledStatus



def say_hello(chat, **kargs):
    chat.sendMessage("Welcome, Try /help")

command("/start", say_hello,
        help_description="Initialize modules", execution_preference=-1)