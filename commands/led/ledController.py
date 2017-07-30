"""File for interaction with fisical leds."""


import os
from commands import command

if os.uname().machine == "armv7l":
    print("Running on raspberry PI, real gpiozero enabled")
    from gpiozero import LED
else:
    print("Runnong outside raspberry, dummy gpiozero enabled")
    from .gpiozero_dummy import LED


led = LED(17)


def on(user, command_info, **kwargs):
    if command_info.required_rights not in user.privileges:
        user.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return
    led.on()
    user["_last_led_interaction"] = "on"
    user.sendMessage("led on")


def off(user, command_info, **kwargs):
    if command_info.required_rights not in user.privileges:
        user.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return
    led.off()
    user["_last_led_interaction"] = "off"
    user.sendMessage("led off")


def control(user, message, command_info, **kwargs):
    if command_info.required_rights not in user.privileges:
        user.sendMessage("You don't have rights to use the Led\nAsk for " +
                         command_info.required_rights + " access to an Admin.")
        return
    if len(message) != 2:
        user.sendMessage(command_info.help_use_hint)
        return
    if message[1] == "on":
        on(user, **kwargs)
    if message[1] == "off":
        off(user, **kwargs)


def status(user, **kwargs):
    last_interaction = user["_last_led_interaction"]
    if last_interaction:
        user.sendMessage(last_interaction)
    else:
        user.sendMessage("Not defined")


PRIVILEGE_NAME = "Led"
command("/ledon", on, required_rights=PRIVILEGE_NAME,
        help_description="Turn on the led")
command("/ledoff", off, required_rights=PRIVILEGE_NAME,
        help_description="Turns off the led")
command("/ledstatus", status, required_rights=PRIVILEGE_NAME,
        help_description="Check the led status")
command("led", control, required_rights=PRIVILEGE_NAME,
        help_description="Use natural language to control the led ",
        help_use_hint="Examples: led on, led off")
