import sqlite3
import threading
import time

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS ticks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    qty REAL
);
CREATE INDEX IF NOT EXISTS idx_ticks_symbol_ts ON ticks(symbol, ts);
"""


class DataStore:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute('PRAGMA journal_mode=WAL;')
        self._conn.executescript(DB_SCHEMA)
        self._conn.commit()

    def insert_tick(self, ts: int, symbol: str, price: float, qty: float):
        with self._lock:
            self._conn.execute(
                "INSERT INTO ticks (ts, symbol, price, qty) VALUES (?, ?, ?, ?)",
                (int(ts), symbol, float(price), float(qty) if qty is not None else None),
            )
            # commit in batches would be more efficient; keep it simple here
            self._conn.commit()

    def get_ticks(self, symbols, start_ts=None, end_ts=None):
        q = "SELECT ts, symbol, price, qty FROM ticks WHERE symbol IN ({})"
        placeholders = ",".join(["?"] * len(symbols))
        q = q.format(placeholders)
        params = list(symbols)
        if start_ts is not None:
            q += " AND ts >= ?"
            params.append(int(start_ts))
        if end_ts is not None:
            q += " AND ts <= ?"
            params.append(int(end_ts))
        q += " ORDER BY ts ASC"
        with self._lock:
            cur = self._conn.execute(q, params)
            rows = cur.fetchall()
        return rows

    def get_latest_timestamp(self, symbol: str):
        q = "SELECT ts FROM ticks WHERE symbol = ? ORDER BY ts DESC LIMIT 1"
        with self._lock:
            cur = self._conn.execute(q, (symbol,))
            r = cur.fetchone()
        return r[0] if r else None


_DS_SINGLETON = None


def get_datastore(path: str = "./ticks.db"):
    global _DS_SINGLETON
    if _DS_SINGLETON is None:
        _DS_SINGLETON = DataStore(path)
    return _DS_SINGLETON


if __name__ == "__main__":
    # quick smoke test
    ds = get_datastore(":memory:")
    ds.insert_tick(int(time.time() * 1000), "BTCUSDT", 20000.0, 0.01)
    print(ds.get_ticks(["BTCUSDT"]))
