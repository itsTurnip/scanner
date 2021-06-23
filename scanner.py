from time import time

import rdm6300
from rdm6300 import BaseReader

from connector import Connector
from pins import Pinout


class Scanner(BaseReader):
    def __init__(self, serial: str, connector: Connector, pins: Pinout, offline_checks_interval=60, **kwargs):
        self.connector = connector
        self.pins = pins
        self.last_card = None
        self.last_send = None
        self.offline = False
        self.offline_checks_interval = offline_checks_interval
        super().__init__(serial, **kwargs)

    def card_inserted(self, card: rdm6300.CardData):
        if self.last_card == card[0]:
            return
        self.pins.scanned()
        r = self.connector.send_nudes(card)
        if r == None:
            self.offline = True
            self.pins.problem()
        elif r:
            self.pins.ok()
        else:
            self.pins.not_found()
        self.last_card = card[0]
        self.send_offline()

    def close(self):
        self.connector.close()
        super().close()

    def send_offline(self):
        if self.connector.send_offline():
            self.offline = False
        self.last_send = time()

    def tick(self):
        if self.offline and time() - self.last_send > self.offline_checks_interval:
            self.send_offline()
