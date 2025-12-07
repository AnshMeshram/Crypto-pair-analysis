import sqlite3
import time

DB = 'ticks.db'

def summarize():
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT symbol, COUNT(*) FROM ticks GROUP BY symbol ORDER BY symbol")
        rows = cur.fetchall()
        if not rows:
            print('No rows found in ticks table yet.')
        else:
            for sym, cnt in rows:
                print(f"{sym}: {cnt}")
    except Exception as e:
        print('Error reading DB:', e)

if __name__ == '__main__':
    # do a few quick polls
    for i in range(6):
        print(f'Poll {i+1}:')
        summarize()
        time.sleep(2)
