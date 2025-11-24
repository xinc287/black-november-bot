# dashboard.py
import streamlit as st
import ccxt
import pandas as pd

API_KEY = "aynı_key"
API_SECRET = "aynı_secret"

exchange = ccxt.binance({'apiKey': API_KEY, 'secret': API_SECRET, 'options': {'defaultType': 'future'}})

st.title("Black November – Gerçek Hesap Canlı Panel")
bal = exchange.fetch_balance()
st.metric("Bakiye", f"${bal['USDT']['total']:,.0f}")

pos = [p for p in exchange.fetch_positions() if float(p['contracts'])>0]
if pos:
    st.dataframe(pd.DataFrame(pos)[['symbol','side','contracts','entryPrice','unrealizedPnl']])
else:
    st.success("Pozisyon yok – sinyal bekleniyor")