
import sys
import time
import TelegramBotCommands
from TelegramBotCommands import BaseCommand
import led

TOKEN = sys.argv[1]  # get token from command-line
TIMEOUT = 60

TelegramBotCommands.Start(TOKEN, TIMEOUT)

@BaseCommand.register("/helloworld")
def hello_world(chat, **kwargs):
    chat.sendMessage("hello world")

while 1:
    time.sleep(10)