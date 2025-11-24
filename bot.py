# bot.py
import ccxt
import pandas as pd
import talib
import time
import logging
from datetime import datetime

# BURAYI DOLDUR
API_KEY = "kendi_binance_api_keyini_yapıştır"
API_SECRET = "kendi_secretini_yapıştır"

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT"]
RISK = 0.017   # %1.7
LEV = 15
MAX_POS = 4

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

def get_df(symbol, tf='5m'):
    bars = exchange.fetch_ohlcv(symbol, tf, limit=300)
    df = pd.DataFrame(bars, columns=['ts','o','h','l','c','v'])
    return df

while True:
    positions = exchange.fetch_positions(SYMBOLS)
    open_count = sum(1 for p in positions if float(p['contracts']) > 0)

    if open_count >= MAX_POS:
        time.sleep(30)
        continue

    for s in SYMBOLS:
        try:
            df = get_df(s)
            c = df['c'].iloc[-1]
            atr = talib.ATR(df['h'], df['l'], df['c'], 14).iloc[-1]
            ema8 = talib.EMA(df['c'], 8).iloc[-1]
            ema21 = talib.EMA(df['c'], 21).iloc[-1]
            rsi = talib.RSI(df['c'], 14).iloc[-1]

            # basit ama çok güçlü sinyal
            if (ema8 > ema21 and df['c'].iloc[-2] <= df['c'].rolling(21).mean().iloc[-2] and rsi < 65):
                balance = exchange.fetch_balance()['USDT']['free']
                qty = (balance * RISK / atr) * LEV
                exchange.set_leverage(LEV, s)
                exchange.create_market_buy_order(s, qty)
                logging.info(f"BUY {s} {qty:.4f} @ {c}")
                print(f"ALIM → {s} {qty:.4f}")

            if (ema8 < ema21 and df['c'].iloc[-2] >= df['c'].rolling(21).mean().iloc[-2] and rsi > 35):
                balance = exchange.fetch_balance()['USDT']['free']
                qty = (balance * RISK / atr) * LEV
                exchange.set_leverage(LEV, s)
                exchange.create_market_sell_order(s, qty)
                logging.info(f"SELL {s} {qty:.4f} @ {c}")
                print(f"SATIM → {s} {qty:.4f}")

            time.sleep(8)
        except:
            pass

    time.sleep(45)