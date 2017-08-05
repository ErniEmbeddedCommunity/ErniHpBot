class LED:
    """dummy led class for debug"""
    def __init__(self, pin):
        self.pin = pin
    def on(self):
        print(str(self.pin)+"_on")

    def off(self):
        print(str(self.pin)+"_off")
