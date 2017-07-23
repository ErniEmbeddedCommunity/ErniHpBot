"""File for interaction with fisical leds."""

import os
# print("os name " + os.uname().machine)
if os.uname().machine == "armv7l":
    print("Running on raspberry PI, real gpiozero enabled")
    from gpiozero import LED    
else:
    print("Runnong outside raspberry, dummy gpiozero enabled")
    from gpiozero_dummy import LED

led = LED(17)
def on():
    led.on()
def off():
    led.off()