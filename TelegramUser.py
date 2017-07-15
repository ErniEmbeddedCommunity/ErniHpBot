"""
This file contais the definition of TUser class
"""
from telepot.loop import MessageLoop

class TUser(MessageLoop):
    """handles the data for each user"""
    def __init__(self):
        self.Name = ""
        self.TelegramID = 0
        self.UserName = ""
