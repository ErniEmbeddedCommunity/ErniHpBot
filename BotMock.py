"""Telegram Bot Wrapper"""
import telepot
from telepot.namedtuple import  InlineKeyboardButton, \
                                InlineKeyboardMarkup, \
                                ReplyKeyboardMarkup, \
                                KeyboardButton
from telepot            import  flavor
from BDMock            import  BDWrapper

class BotWrapper:
    """Functios for managing the conection to the bot"""
    def __init__(self, token: str):
        """ Class oriented methods"""
        print("Bot token is " +  token)
        self.__bot = telepot.Bot(token)
        print('I am alive')

    def __enter__(self):
        print('I enter')

    def __exit__(self, exc_type, exc_value, traceback):
        print('I am dead')
    @staticmethod
    def sayhello(msg):
        """print a msg"""
        print(msg)

# Functions based on telepot source code
#########################################

    def add_handle(self, handle):
        """ Link function to process all incomming mensages"""
        self.__bot.message_loop(handle)

    @staticmethod
    def get_flavor(message):
        """ Determines the type of message received"""
        return flavor(message)

    def send_message(self, chat_id, message):
        """ Function to send a text message"""
        self.__bot.sendMessage(chat_id, message)

    def send_reply(self, chat_id, message):
        """ Function to send a callback reply"""
        self.__bot.answerCallbackQuery(chat_id, text=message)

    @staticmethod
    def new_inlinebutton(label, reply):
        """ Retrieves a button structure for inline keyboard"""
        return InlineKeyboardButton(text=label, callback_data=reply)

    @staticmethod
    def new_inlinekeyboard(buttons, n_cols):
        """ Retrieves a inline keyboard using on a list of buttons"""
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        return InlineKeyboardMarkup(inline_keyboard=menu)

    @staticmethod
    def new_custombutton(label):
        """ Retrieves a button structure for custom keyboard"""
        return KeyboardButton(text=label)

    @staticmethod
    def new_customkeyboard(buttons, n_cols):
        """ Retrieves a custom keyboard using on a list of buttons"""
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        return ReplyKeyboardMarkup(keyboard=menu)

    def send_keyboard(self, chat_id, message, keyboard):
        """ Sends structure keyboard to chat"""
        self.__bot.sendMessage(chat_id, message, reply_markup=keyboard)

class Chat:
    """Handles chat data."""
    def __init__(self, telegram_id: str):
        pass

    def send_msg(self, msg: str):
        """Send Telegram msg to the chat."""
        pass
    def send_keyboard(self, keyboard):
        """Sends a keyboard to the chat"""
        pass
    def save_chat(self):
        """Stores the information related to this chat in the database"""
        pass


    @staticmethod
    def get_chat_by_id(telegram_id: int):
        """Return the chat id identified by his unique Telegram ID."""
        pass

    @staticmethod
    def handle_new_msg(telegram_msg: dict):
        """handles a new msg."""
        pass


class User:
    """Handles user data"""
    
    active_users_count  = dict()
    active_users = dict()
    DB = BDWrapper.getDB()

    @classmethod
    def create_user_by_Id(cls, telegramid):
        
        if telegramid["id"] in cls.active_users_count:
            cls.active_users_count[telegramid["id"]] += 1
        else:
            cls.active_users_count[telegramid["id"]] = 1
            cls.active_users[telegramid["id"]] = User(telegramid)

        return cls.active_users[telegramid["id"]]

    @classmethod
    def dispose_user_by_id(cls, telegramid):
        cls.active_users_count[telegramid] -= 1
        if cls.active_users_count[telegramid] == 0:
            cls.active_users_count.pop(telegramid)
            user = cls.active_users.pop(telegramid)
            user.save()



    def __init__(self, telegramUser: dict):
        self._telegramUser = telegramUser
        self.privileges = set()
        self.last_msg = ""


        self.load()

    def get_last_msg(self):
        return self.last_msg
    def set_last_msg(self, msg: str):
        self.last_msg = msg

    def checkForPrivileges(self, privilege: str):
        if privilege in self.privileges:
            return True
        else:
            return False

    def save(self):
        self.DB.set_key_value(str(self._telegramUser["id"])+"_last_msg", self.last_msg)
        self.DB.set_key_value(str(self._telegramUser["id"])+"_privileges", ",".join(self.privileges))
    def load(self):
        byte_last_msg = self.DB.get_key_value(str(self._telegramUser["id"])+"_last_msg")
        if byte_last_msg != None:
            self.last_msg = byte_last_msg.decode("utf-8")

        byte_privileges = self.DB.get_key_value(str(self._telegramUser["id"])+"_privileges")
        if byte_privileges != None:
            self.privileges = set(byte_privileges.decode("utf-8").split(","))


