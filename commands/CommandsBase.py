""" This file includes the definition for base command classes """
import re
import TelegramUser
from enum import Enum


class HandledStatus(Enum):
    """ 
    HANDLED  = Mark as handled but continues to the end.
    NOT_HANDLED = Mark as not handled and continue to the end,
    HANDLED_BREAK = Mark as handled and breaks, the commands 
                    with less execution preference won't 
                    recive this message
    """
    HANDLED = 0,
    NOT_HANDLED = 1,
    HANDLED_BREAK = 2


def redirect_msg(msg, user):
    handled = HandledStatus.NOT_HANDLED
    for command in _registered_commands:
        try:
            msg_match = command._check_if_msg_match(
                telegram_message=msg, user=user)
            if msg_match != None:
                result = command.do_action(message=msg_match,
                                           user=user, telegram_message=msg, handled=handled)
                
                if isinstance(result, HandledStatus):
                    handled = result
                elif result is None:
                    handled = HandledStatus.HANDLED
                else:
                    raise TypeError("do_action function returns an invalid value type")
        except Exception as ex:
            print(ex)


_registered_commands = list()


def get_execution_preference(command):
    return command.execution_preference * -1


class command():
    """
    creates a telegram command

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
    the function must return the handled status for the command in order
    to allow other command instances to interact with it.
    by default, if you don't return a value but the command matchs.
    it will be register as handled.


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
    """

    def __init__(self, command_name, do_action,
                 help_description="", help_group="", help_use_hint="",
                 execution_preference=0, required_rights=""):
        self.help_description = help_description
        self.help_group = help_group
        self.help_use_hint = help_use_hint
        self.required_rights = required_rights
        self.command_name = command_name
        self._do_action = do_action
        self.execution_preference = execution_preference
        _registered_commands.append(self)
        _registered_commands.sort(key=get_execution_preference)

    def _check_if_msg_match(self, telegram_message, user):
        if "text" not in telegram_message:
            return
        message = telegram_message["text"].replace('_',' ')
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

    def do_action(self, message, user, telegram_message, handled):
        return self._do_action(message=message, user=user,
                        telegram_message=telegram_message, handled=handled, command_info=self)

    def __str__(self):
        return self.command_name + ": " + self.help_description

    def __repr__(self):
        return self.__str__()


class pattern_command(command):
    """
    Basically the same as command but matches de text with a regex expression
    """
    def __init__(self, command_pattern, do_action, command_name="",
                 help_description="", help_group="", help_use_hint="",
                 execution_preference=0, required_rights=""):
        self._command_pattern = re.compile(command_pattern)
        if command_name == "":
            command_name = command_pattern
        super().__init__(command_name=command_name, do_action=do_action,
                 help_description=help_description, help_group=help_group, help_use_hint=help_use_hint,
                 execution_preference=execution_preference, required_rights=required_rights)

    def _check_if_msg_match(self, telegram_message, user):
        if "text" not in telegram_message:
            return
        match = self._command_pattern.match(telegram_message["text"])
        if match:
            return match.groups()
        return None
