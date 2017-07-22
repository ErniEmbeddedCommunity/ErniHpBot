"""Telegram Bot Wrapper"""
import pickle
import telepot
from telepot.namedtuple import  InlineKeyboardButton, \
                                InlineKeyboardMarkup, \
                                ReplyKeyboardMarkup, \
                                KeyboardButton
from telepot            import  flavor
from BDMock            import  BDWrapper
from threading import Lock

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
    """Handles group chat data."""
    active_chats_count = dict()
    active_chats = dict()

    DB = BDWrapper.getDB()
    DBLocker = Lock()

    @classmethod
    def create_chat_by_id(cls, telegramchat):
        """Return the chat id identified by his unique Telegram ID."""
        cls.DBLocker.acquire()
        if telegramchat["id"] in cls.active_chats_count:
            cls.active_chats_count[telegramchat["id"]] += 1
        else:
            cls.active_chats_count[telegramchat["id"]] = 1
            cls.active_chats[telegramchat["id"]] = Chat(telegramchat)
        cls.DBLocker.release()
        return cls.active_chats[telegramchat["id"]]

    @classmethod
    def dispose_chat_by_id(cls, telegramchat):
        """
        Disposes the chat information and stores it in the database.
        Only if its the last object in use.
        """
        cls.DBLocker.acquire()
        cls.active_chats_count[telegramchat] -= 1
        if cls.active_chats_count[telegramchat] == 0:
            cls.active_chats_count.pop(telegramchat)
            chat = cls.active_chats.pop(telegramchat)
            chat.save()
        cls.DBLocker.release()


    def __init__(self, telegram_chat):
        self._telegram_chat = telegram_chat
        self.users = set()

        self.load()

    def update_chat(self, telegram_chat):
        """Updates the internal information each time a new msg is received"""
        self.telegram_chat = telegram_chat

    def add_user(self, telegram_user):
        """stores the user id in the set of group users"""
        self.users.add(telegram_user["id"])

    def save(self):
        """Stores the information related to this chat in the database"""
        serialized_object = pickle.dumps(self._telegram_chat)
        self.DB.set_key_value(str(self._telegram_chat["id"])+"_telegram_chat",serialized_object)
        serialized_object = pickle.dumps(self.users)
        self.DB.set_key_value(str(self._telegram_chat["id"])+"_users",serialized_object)

    def load(self):
        """Load the information from the database."""
        byte_telegram_chat = self.DB.get_key_value(str(self._telegram_chat["id"])+"_telegram_chat")
        if byte_telegram_chat != None:
            self._telegram_chat = pickle.loads(byte_telegram_chat)
        byte_users = self.DB.get_key_value(str(self._telegram_chat["id"])+"_users")
        if byte_users != None:
            self.users = pickle.loads(byte_users)

class User:
    """Handles user data"""
    
    active_users_count  = dict()
    active_users = dict()
    DB = BDWrapper.getDB()

    DBLocker = Lock()
    @classmethod
    def create_user_by_Id(cls, telegramid):
        """
        Creates a new user from the data stored in the database 
        or if it already exist
        Returns the current user in use
        """ 
        cls.DBLocker.acquire()
        if telegramid["id"] in cls.active_users_count:
            cls.active_users_count[telegramid["id"]] += 1
        else:
            cls.active_users_count[telegramid["id"]] = 1
            cls.active_users[telegramid["id"]] = User(telegramid)
        cls.DBLocker.release()
        return cls.active_users[telegramid["id"]]

    @classmethod
    def dispose_user_by_id(cls, telegramid):
        """
        Destroys the user information and stores it in the data base
        or if there is any other object using it
        Decrements the reference count
        """

        cls.DBLocker.acquire()
        cls.active_users_count[telegramid] -= 1
        if cls.active_users_count[telegramid] == 0:
            cls.active_users_count.pop(telegramid)
            user = cls.active_users.pop(telegramid)
            user.save()
        cls.DBLocker.release()


    def __init__(self, telegramUser: dict):
        self._telegram_user = telegramUser
        self.privileges = set()
        self.groups = set()
        self.last_msg = ""

        self.load()

    def get_last_msg(self):
        return self.last_msg
    def set_last_msg(self, msg: str):
        self.last_msg = msg

    def checkForPrivileges(self, privilege: set):
        if privilege in self.privileges:
            return True
        else:
            return False

    def update_telegram_user(self, telegram_user):
        self._telegram_user = telegram_user

    def add_group(self, chat: Chat):
        self.groups.add(chat)

    def id(self):
        return self._telegram_user["id"]

    def save(self):
        """Stores the data in the database"""
        self.DB.set_key_value(str(self._telegram_user["id"])+"_last_msg", self.last_msg)
        self.DB.set_key_value(str(self._telegram_user["id"])+"_privileges", ",".join(self.privileges))
        serialized_object = pickle.dumps(self._telegram_user)
        self.DB.set_key_value(str(self._telegram_user["id"])+"_telegramUser",serialized_object)
        serialized_object = pickle.dumps(self.groups)
        self.DB.set_key_value(str(self._telegram_user["id"])+"_groups",serialized_object)

    def load(self):
        """Loads the data from the database"""
        byte_last_msg = self.DB.get_key_value(str(self._telegram_user["id"])+"_last_msg")
        if byte_last_msg != None:
            self.last_msg = byte_last_msg.decode("utf-8")

        byte_privileges = self.DB.get_key_value(str(self._telegram_user["id"])+"_privileges")
        if byte_privileges != None:
            self.privileges = set(byte_privileges.decode("utf-8").split(","))

        byte_telegram_user = self.DB.get_key_value(str(self._telegram_user["id"])+"_telegramUser")
        if byte_telegram_user != None:
            self._telegram_user = pickle.loads(byte_telegram_user)

        byte_groups = self.DB.get_key_value(str(self._telegram_user["id"])+"_groups")
        if byte_groups != None:
            self.groups = pickle.loads(byte_groups)


