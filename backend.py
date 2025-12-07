import asyncio
import json
import threading
import time
from typing import List

import websockets

from data_store import get_datastore


class BinanceIngest:
    def __init__(self, symbols: List[str], db_path: str = "./ticks.db"):
        self.symbols = [s.lower() for s in symbols]
        self.ds = get_datastore(db_path)
        self._thread = None
        self._stop_event = threading.Event()

    def _combined_stream_url(self):
        streams = "/".join([f"{s}@trade" for s in self.symbols])
        return f"wss://stream.binance.com:9443/stream?streams={streams}"

    async def _consumer(self):
        uri = self._combined_stream_url()
        async with websockets.connect(uri) as ws:
            while not self._stop_event.is_set():
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                except asyncio.TimeoutError:
                    continue
                data = json.loads(msg)
                # combined stream wraps payload in 'data'
                if "data" in data:
                    d = data["data"]
                else:
                    d = data
                # trade event expected fields
                try:
                    ts = int(d.get("T") or d.get("E") or int(time.time() * 1000))
                    symbol = d.get("s")
                    price = float(d.get("p"))
                    qty = float(d.get("q") or d.get("Q") or 0)
                except Exception:
                    continue
                # store
                self.ds.insert_tick(ts, symbol, price, qty)

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._consumer())
            except Exception:
                pass

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)


if __name__ == "__main__":
    bi = BinanceIngest(["BTCUSDT", "ETHUSDT"]) 
    bi.start()
    print("Ingesting for 10s...")
    time.sleep(10)
    bi.stop()
