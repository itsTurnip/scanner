from configparser import ConfigParser

from connector import Connector
from pins import Pinout
from scanner import Scanner

DEFAULT_CONFIG_PATH = "./config.ini"


def main():
    config = ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)
    server = config['SERVER']
    pins = config['PINS']
    scan = config['SCAN']

    connector = Connector(**server)
    pinout = Pinout(pins['led'], pins['buzzer'])
    scanner = Scanner(scan['port'], connector, pinout, heartbeat_interval=1)
    scanner.send_offline()
    try:
        scanner.start()
    except KeyboardInterrupt:
        scanner.close()


if __name__ == "__main__":
    main()
