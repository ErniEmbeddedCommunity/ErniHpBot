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
    def __init__(self, db: BDWrapper):
        """ Class oriented methods"""
        ## Load token form data base
        token = db.get_key_value("Token")
        #check if its valid
        if token is None:
            #Request a new one
            token = input("Write the bot token")
            #save it
            db.set_key_value("Token", token)
        #request the token again and decode it to a string
        token = db.get_key_value("Token").decode("utf-8")
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
