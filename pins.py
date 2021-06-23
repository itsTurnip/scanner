from time import sleep

from gpiozero import LED, Buzzer

TIME = 0.1


class Pinout:
    def __init__(self, led: int, buzzer: int):
        self.led = LED(led)
        self.buzzer = Buzzer(buzzer)

    def both_on(self):
        self.led.on()
        self.buzzer.on()

    def both_off(self):
        self.led.off()
        self.buzzer.off()

    def both_toggle(self, time):
        self.both_on()
        sleep(time)
        self.both_off()

    def scanned(self):
        self.both_toggle(TIME)

    def not_found(self):
        self.both_toggle(TIME)
        sleep(TIME / 2)
        self.both_toggle(TIME)

    def ok(self):
        self.both_toggle(TIME)

    def problem(self):
        self.both_toggle(TIME)
        sleep(TIME / 2)
        self.both_toggle(TIME * 3)
