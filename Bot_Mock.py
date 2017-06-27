import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telepot            import flavor


class Bot_wrapper:

    def __init__(self):
        """ Class oriented methods"""
        self.__bot = telepot.Bot('TOKEN-KEY-HERE')
        print ('I am alive')

    def __enter__(self):
        print ('I enter')

    def __exit__(self, exc_type, exc_value, traceback):
        print ('I am dead')

    def sayhello(self, msg):
        print (msg)

# Functions based on telepot source code
#########################################

    def add_handle(self, handle):
        """ Link function to process all incomming mensages"""
        self.__bot.message_loop(handle)

    def get_flavor(self, message):
        """ Determines the type of message received"""
        return flavor(message)

    def send_message(self, chat_id, message):
        """ Function to send a text message"""
        self.__bot.sendMessage(chat_id, message)

    def send_reply(self, chat_id, message):
        """ Function to send a callback reply"""
        self.__bot.answerCallbackQuery(chat_id,text=message)

    def new_inlinebutton(self, label, reply):
        """ Retrieves a button structure for inline keyboard"""
        return InlineKeyboardButton(text=label,callback_data=reply)

    def new_inlinekeyboard(self, buttons, n_cols):
        """ Retrieves a inline keyboard using on a list of buttons"""
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        return InlineKeyboardMarkup(inline_keyboard=menu)

    def new_custombutton(self, label):
        """ Retrieves a button structure for custom keyboard"""
        return KeyboardButton(text=label)

    def new_customkeyboard(self, buttons, n_cols):
        """ Retrieves a custom keyboard using on a list of buttons"""
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        return ReplyKeyboardMarkup(keyboard=menu)

    def send_keyboard(self, chat_id, message, keyboard):
        """ Sends structure keyboard to chat"""
        self.__bot.sendMessage(chat_id, message, reply_markup=keyboard)


