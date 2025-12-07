import time
from backend import BinanceIngest

if __name__ == '__main__':
    bi = BinanceIngest(["BTCUSDT", "ETHUSDT"], db_path='ticks.db')
    print('Starting ingest for 20s... (press Ctrl+C to stop)')
    bi.start()
    try:
        time.sleep(20)
    except KeyboardInterrupt:
        pass
    bi.stop()
    print('Ingest stopped')
