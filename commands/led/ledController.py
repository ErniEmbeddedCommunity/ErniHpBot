"""File for interaction with fisical leds."""


import os
from commands import command,KeyboardCommand
from ..tools.UserPrivileges import check_for_access

if os.uname().machine == "armv7l":
    print("Running on raspberry PI, real gpiozero enabled")
    from gpiozero import LED
else:
    print("Runn.ong outside raspberry, dummy gpiozero enabled")
    from .gpiozero_dummy import LED


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

def enable_control(user, chat, command_info, **kwargs):
    if check_for_access(user, command_info):
        chat.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return

    ledkeyboard.send(chat)
def control(user, chat, key, command_info, **kwargs):
    if key == "on":
        on(user, chat, command_info, **kwargs)
        ledkeyboard.send(chat, "OK")
    if key == "off":
        off(user, chat, command_info, **kwargs)
        ledkeyboard.send(chat, "OK")
    if key == "quit":
        chat.sendMessage("Ok")
    if key == None:
        ledkeyboard.send(chat)


def status(user, chat, **kwargs):
    last_interaction = user["_last_led_interaction"]
    if last_interaction:
        chat.sendMessage(last_interaction)
    else:
        chat.sendMessage("Not defined")


PRIVILEGE_NAME = "Led"
command("/ledon", on, required_rights=PRIVILEGE_NAME,
        help_description="Turn on the led")
command("/ledoff", off, required_rights=PRIVILEGE_NAME,
        help_description="Turns off the led")
command("/ledstatus", status, required_rights=PRIVILEGE_NAME,
        help_description="Check the led status")
command("/led", enable_control, required_rights=PRIVILEGE_NAME,
        help_description="Enable the keyboard")
ledkeyboard = KeyboardCommand([["on", "off"], ["quit"]], control, "Use the keyboard")
