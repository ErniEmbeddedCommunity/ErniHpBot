"""File for interaction with fisical leds."""


import os
from TelegramBotCommands import BaseCommand, Keyboard
from TelegramBotCommands.Tools.UserPrivileges import check_for_access

try:
    from gpiozero import LED
    print("Running on raspberry PI, real gpiozero enabled")
except ImportError as ex:
    from .gpiozero_dummy import LED
    print("Runn.ong outside raspberry, dummy gpiozero enabled")


PRIVILEGE_NAME = "Led"
LED_KEYBOARD = Keyboard()
led = LED(17)


def on(user, chat, command_info, **kwargs):
    if check_for_access(user, command_info):
        chat.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return
    led.on()
    user["_last_led_interaction"] = "on"
    chat.sendMessage("led on")


def off(user, chat, command_info, **kwargs):
    if check_for_access(user, command_info):
        chat.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return
    led.off()
    user["_last_led_interaction"] = "off"
    chat.sendMessage("led off")


@BaseCommand.register("/led",
                      required_rights=PRIVILEGE_NAME,
                      help_description="Enable the keyboard")
def enable_control(user, chat, command_info, **kwargs):
    if check_for_access(user, command_info):
        chat.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return

    LED_KEYBOARD.send(chat, "Use the keyboard" ,[["on", "off"], ["quit"]], control)


def control(user, chat, key, command_info, **kwargs):
    if key == "on":
        on(user, chat, command_info, **kwargs)
        LED_KEYBOARD.send(chat, "OK" ,[["on", "off"], ["quit"]], control)
    if key == "off":
        off(user, chat, command_info, **kwargs)
        LED_KEYBOARD.send(chat, "OK" ,[["on", "off"], ["quit"]], control)
    if key == "quit":
        chat.sendMessage("Ok")
    if key is None:
        LED_KEYBOARD.send(chat, "Use the keyboard" ,[["on", "off"], ["quit"]], control)


@BaseCommand.register("/ledstatus",
                      required_rights=PRIVILEGE_NAME,
                      help_description="Check the led status")
def status(user, chat, **kwargs):
    last_interaction = user["_last_led_interaction"]
    if last_interaction:
        chat.sendMessage(last_interaction)
    else:
        chat.sendMessage("Not defined")





