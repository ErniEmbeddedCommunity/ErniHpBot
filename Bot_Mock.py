import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telepot            import flavor


class Bot_wrapper:

# Class oriented methods
########################
  def __init__(self):
  	self.__bot = telepot.Bot('TOKEN-KEY-HERE')
  	print 'I am alive'

  def __enter__(self):
    print 'I enter'

  def __exit__(self, exc_type, exc_value, traceback):
    print 'I am dead'

  def sayhello(self, msg):
    print msg

# Functions based on telepot source code
#########################################

  # Link function to process all incomming mensages
  #################################################
  def add_handle(self, handle):
  	self.__bot.message_loop(handle)

  # Determines the type of message received
  #########################################
  def get_flavor(self, message):
    return flavor(message)

  # Function to send a text message
  #################################
  def send_message(self, chat_id, message):
  	self.__bot.sendMessage(chat_id, message)

  # Function to send a callback reply
  ###################################
  def send_reply(self, chat_id, message):
    self.__bot.answerCallbackQuery(chat_id,text=message)

  # Retrieves a button structure for inline keyboard
  ##################################################
  def new_inlinebutton(self, label, reply):
	  return InlineKeyboardButton(text=label,callback_data=reply)

  # Retrieves a inline keyboard using on a list of buttons
  ########################################################
  def new_inlinekeyboard(self, buttons, n_cols):
	  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	  return InlineKeyboardMarkup(inline_keyboard=menu)

  # Retrieves a button structure for custom keyboard
  ##################################################
  def new_custombutton(self, label):
    return KeyboardButton(text=label)

  # Retrieves a custom keyboard using on a list of buttons
  ########################################################
  def new_customkeyboard(self, buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return ReplyKeyboardMarkup(keyboard=menu)

  # Sends structure keyboard to chat
  ##################################
  def send_keyboard(self, chat_id, message, keyboard):
	  self.__bot.sendMessage(chat_id, message, reply_markup=keyboard)


