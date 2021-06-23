import logging
import sqlite3
from datetime import datetime
from typing import Union

import rdm6300
import requests
from requests.exceptions import ConnectionError, Timeout

TIMEOUT = 1.5


class Connector:
    def __init__(self, host, token, db_path="offline.db"):
        self.host = host
        self.token = token

        self.db = self._init_db(db_path)

        self.session = requests.Session()
        self.session.headers["Authorization"] = self.token
        self.session.headers["Content-Type"] = "application/json"

    @staticmethod
    def _init_db(db_path) -> sqlite3.Connection:
        conn = sqlite3.connect(
            db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        with conn:
            cur = conn.cursor()
            cur.execute(
                'CREATE TABLE IF NOT EXISTS "Cards" ("card_id" INTEGER, "timestamp" INTEGER);')
            conn.commit()
            cur.close()
        return conn

    def send_nudes(self, card_info: rdm6300.CardData) -> Union[bool, None]:
        card = card_info[0]
        now = datetime.now()
        data = ({"time": now.isoformat(), "card": card},)
        try:
            r = self.session.post(self.host, json=data, timeout=TIMEOUT)
        except (Timeout, ConnectionError) as e:
            logging.error(e)
            self.save_offline(card, now)
            return None
        if r.status_code == 200:
            return True
        elif r.status_code == 204:
            return False

    def close(self):
        self.db.close()

    def send_offline(self) -> bool:
        with self.db as db:
            cur = db.cursor()
            rows = cur.execute(
                'SELECT "card_id", "timestamp" as "ts [timestamp]" FROM "Cards";')

            def zipping(row):
                return dict(
                    zip(("card", "time"), (row[0], row[1].isoformat())))

            rows = list(map(zipping, rows))
            if rows:
                try:
                    r = self.session.post(
                        self.host, json=rows, timeout=TIMEOUT)
                    if r.status_code == 200:
                        cur.execute('DELETE FROM "Cards"')
                except (Timeout, ConnectionError) as e:
                    logging.error(e)
                    return False
            return True

    def save_offline(self, card_id: int, time: datetime):
        with self.db as db:
            cur = db.cursor()
            cur.execute("INSERT INTO Cards VALUES (?, ?);", (card_id, time))
            cur.close()
