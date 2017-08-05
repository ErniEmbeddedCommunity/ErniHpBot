""" This file includes the definition for base command classes """
import re
# from .TelegramUser import TUser
from enum import Enum
from .TelegramUser import TChat, TUser, TGroup


class HandledStatus(Enum):
    """ 
    HANDLED  = Mark as handled but continues to the end.
    NOT_HANDLED = Mark as not handled and continue to the end,
    HANDLED_BREAK = Mark as handled and breaks, the commands 
                    with less execution preference won't 
                    recive this message
    """
    HANDLED = 0
    NOT_HANDLED = 1
    HANDLED_BREAK = 2


class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"


_registered_commands = list()
def redirect_msg(msg, user, chat):
    handled = HandledStatus.NOT_HANDLED
    for command in _registered_commands:
        try:
            msg_match = command._check_if_msg_match(
                telegram_message=msg, user=user, chat=chat)
            if msg_match != None:
                result = command.do_action(message=msg_match,
                                           user=user, chat=chat,
                                           telegram_message=msg, handled=handled)

                if isinstance(result, HandledStatus):
                    handled = result
                elif result is None:
                    handled = HandledStatus.HANDLED
                else:
                    raise TypeError(
                        "do_action function returns an invalid value type")
                if handled == HandledStatus.HANDLED_BREAK:
                    break
        except Exception as ex:
            print(ex)




class BaseCommand():
    """
    creates a telegram command
    @param command_name: Command identification name
    @param do_action: Callback function when the command is executed.
    @param help_description: Description for help menu,
                             if the command doesn't have description 
                             it will be hiden in the help menu.
    @param help_grou: FUTURE USE, intended to sort help menu by groups
    @param help_use_hint: Example of usage, usually sent to the user
                          when he makes an error calling the command.
    @param execution_preference: higher = get called before other commands
                                commands with the same prefence will be 
                                executed in undefined order
    @param required_rights: helps to standardize access control to commands 
                            and (FUTURE) hide commands from help menu
                            if you can use them
    @param available_in: select the kind of chat where the command is available.
    @param enabled_for_user: if None, enabled for everyone
                             if set(TUsers), enabled only for users in this set.

    The do_action function gets the following information:
        @param message = return value for _check_if_msg_match, 
                        in this case a list with all the words 
                        in the message just like message.split()
        @param user = TUser instance for the sender.
        @param telegram_message= message strunct received from telegram,
                                you can get a lot of usefull information 
                                but with message if often enough
        @param handled = (ON DEVELOPMEN)
        @param command_info= command instance for the current command.
                            you can get information for rights or help
                            hits from this.
        @return = The function must return the handled status for the command in order
                    to allow other command instances to interact with it.
                    by default, if you don't return a value but the command matchs.
                    it will be register as handled.
    the execution_preference is 0 by default and I decided to follow this rule:
        10 -> high preference commands with no blocking actions, (like a global msg log)
        5 -> high preference commands with blocking actions, (like a keyboard)
        4 -> Error catch for level 5, (catch non keyborad msg and block)
        0 -> normal commands with no care about execution order (like /help)
        -1 -> Error catch for normal commands
        -5 -> Detect type erros in commands and send help to the user (TODO)
        -10 -> general detect Not handled commands and send a response (Try /help msg)

    """
    @classmethod
    def register(cls,
                 command_name,
                 help_description="",
                 help_group="",
                 help_use_hint="",
                 execution_preference=0,
                 required_rights="",
                 available_in=set(
                     {ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}),
                 enabled_key=None
                 ):
        """
        This functions is intended to be used as a decorator.
        Creates and registers a command.
        if for any reason, you need to havea access to the command instance,
        you can call this function directly and get the second return parameter.
        see an example in the implementation of Keyboard.
        """
        def return_function(do_action):
            new_command = BaseCommand(command_name,
                                      do_action,
                                      help_description,
                                      help_group,
                                      help_use_hint,
                                      execution_preference,
                                      required_rights,
                                      available_in,
                                      enabled_key
                                      )
            new_command.add_to_registered_list()
            return do_action, new_command
        return return_function

    def add_to_registered_list(self):
        """
        Add this command to the registerd command list.
        this function is called automatically in the register function
        Don't add the command multiple times
        """
        _registered_commands.append(self)
        _registered_commands.sort(key=self.get_execution_preference)

    def remove_from_registered_list(self):
        """
        Remove this command from the registered command list. 
        If you want to temporally disable the command use enabled_key insted
        """
        _registered_commands.remove(self)

    @staticmethod
    def get_execution_preference(command):
        """This function is intended to be use with the sort list command."""
        return command.execution_preference * -1

    def __init__(self,
                 command_name,
                 do_action,
                 help_description="",
                 help_group="",
                 help_use_hint="",
                 execution_preference=0,
                 required_rights="",
                 available_in=set(
                     {ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}),
                 enabled_key=None
                 ):
        self.help_description = help_description
        self.help_group = help_group
        self.help_use_hint = help_use_hint
        self.required_rights = required_rights
        self.command_name = command_name
        self._do_action = do_action
        self.execution_preference = execution_preference
        self.available_in = available_in
        self.enabled_key = enabled_key

    def _common_match_requirements(self, telegram_message, user, chat):
        """ Checks the common requirement for matching."""
        # check if its enabled for all users or just a set of them
        if self.enabled_key is not None:
            if chat.id not in self.enabled_key:
                return False
        # check for message type
        if "text" not in telegram_message:
            return False
        # Check for chat type
        chattype = chat["type"]

        def getvalue(x):
            return x.value
        available_list = list(map(getvalue, self.available_in))
        if chattype not in available_list:
            return False
        return True

    def _check_if_msg_match(self, telegram_message, user, chat):
        if isinstance(chat, TGroup):
            if "@" + chat.bot_username not in telegram_message["text"]:
                return

        if not self._common_match_requirements(telegram_message, user, chat):
            return
        # check for message match
        message = telegram_message["text"].replace('_', ' ')
        message = message.replace("@" + chat.bot_username, "")
        match = message.split()
        if match:
            if match[0].lower() == self.command_name.lower():
                return match
            else:
                return None
        return None
        # if "voice" in telegram_message:
        #     voiceFile = user.bot.getFile(telegram_message["voice"]["file_id"])
        #     return voiceFile

    def do_action(self, message, user, chat, telegram_message, handled):
        return self._do_action(message=message,
                               user=user,
                               chat=chat,
                               telegram_message=telegram_message,
                               handled=handled,
                               command_info=self)

    def __str__(self):
        return self.command_name + ": " + self.help_description

    def __repr__(self):
        return self.__str__()

    def enable_for_user(self, user):
        self.enabled_key.add(user.id)

    def disable_for_user(self, user):
        self.enabled_key.remove(user.id)


class PatternCommand(BaseCommand):
    """
    Basically the same as command but matches de text with a regex expression
    """
    @classmethod
    def register(cls, command_pattern,
                 command_name="",
                 help_description="",
                 help_group="",
                 help_use_hint="",
                 execution_preference=0,
                 required_rights="",
                 available_in=set(
                     {ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}),
                 enabled_key=None
                 ):
        """This functions creates and registers a command."""

        def return_function(do_action):
            new_command = PatternCommand(command_pattern,
                                         do_action, command_name,
                                         help_description,
                                         help_group,
                                         help_use_hint,
                                         execution_preference,
                                         required_rights,
                                         available_in,
                                         enabled_key)
            new_command.add_to_registered_list()
            return do_action, new_command
        return return_function

    def __init__(self,
                 command_pattern,
                 do_action,
                 command_name="",
                 help_description="",
                 help_group="",
                 help_use_hint="",
                 execution_preference=0,
                 required_rights="",
                 available_in=set(
                     {ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}),
                 enabled_key=None
                 ):
        self._command_pattern = re.compile(command_pattern)
        if command_name == "":
            command_name = command_pattern
        super().__init__(command_name=command_name,
                         do_action=do_action,
                         help_description=help_description,
                         help_group=help_group,
                         help_use_hint=help_use_hint,
                         execution_preference=execution_preference,
                         required_rights=required_rights,
                         available_in=available_in,
                         enabled_key=enabled_key)

    def _check_if_msg_match(self, telegram_message, user, chat):
        if not self._common_match_requirements(telegram_message, user, chat):
            return

        match = self._command_pattern.match(telegram_message["text"])
        if match:
            return match.groups()
        return None


class Keyboard():
    """Sends a keyboard and waits for response"""

    callback = dict()
    keyboard = dict()
    # def __init__(self):
    #     self.command = PatternCommand(
    #         "(.*)", self.keypress, execution_preference=4, enabled_key=set())
    #     self.command.add_to_registered_list()

    @classmethod
    def send(cls, chat, text, keyboard, callback):
        cls.callback[chat.id] = callback
        cls.keyboard[chat.id] = keyboard
        cls.command.enable_for_user(chat)
        chat.sendMessage(text, cls.keyboard[chat.id])

    @classmethod
    def keep_instance(cls, pattern_command_instance):
        cls.command = pattern_command_instance

    @staticmethod
    def keypress(chat, message, **kwargs):
        Keyboard.command.disable_for_user(chat)
        key = None
        for rowkey in Keyboard.keyboard[chat.id]:
            if isinstance(rowkey, list):
                for columkey in rowkey:
                    if message[0] == columkey:
                        key = columkey
                        break
                if key is not None:
                    break
            else:
                if message[0] == rowkey:
                    key = rowkey
                    break

        del Keyboard.keyboard[chat.id]
        callback = Keyboard.callback[chat.id]
        del Keyboard.callback[chat.id]

        callback(**kwargs, chat=chat, message=message, key=key)
        return HandledStatus.HANDLED_BREAK

    keypress_decorator, command = PatternCommand.register(
        "(.*)",
        execution_preference=4,
        enabled_key=set()
    )(keypress.__func__)

class InlineKeyboard():
    """Sends a keyboard and waits for response"""

    callback = dict()
    keyboard = dict()
    # def __init__(self):
    #     self.command = PatternCommand(
    #         "(.*)", self.keypress, execution_preference=4, enabled_key=set())
    #     self.command.add_to_registered_list()

    @classmethod
    def send(cls, chat, text, keyboard, callback):
        cls.callback[chat.id] = callback
        cls.keyboard[chat.id] = keyboard
        cls.command.enable_for_user(chat)
        chat.sendMessage(text, inlinekeyboard=cls.keyboard[chat.id])

    @classmethod
    def keep_instance(cls, pattern_command_instance):
        cls.command = pattern_command_instance

    @staticmethod
    def keypress(chat, message, **kwargs):
        print(chat)
        InlineKeyboard.command.disable_for_user(chat)
        key = None
        for rowkey in InlineKeyboard.keyboard[chat.id]:
            if isinstance(rowkey, list):
                for columkey in rowkey:
                    if message[0] == columkey:
                        key = columkey
                        break
                if key is not None:
                    break
            else:
                if message[0] == rowkey:
                    key = rowkey
                    break

        del InlineKeyboard.keyboard[chat.id]
        callback = InlineKeyboard.callback[chat.id]
        del InlineKeyboard.callback[chat.id]

        callback(**kwargs, chat=chat, message=message, key=key)
        return HandledStatus.HANDLED_BREAK

    keypress_decorator, command = PatternCommand.register(
        "/InlineKeyboard_(.*)",
        execution_preference=4,
        enabled_key=set()
    )(keypress.__func__)
