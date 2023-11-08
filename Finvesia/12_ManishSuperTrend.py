import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c  # Same filename of your login python file
import tkinter as tk
from flask import Flask, request
import requests
import numpy as np
import datetime as dt
import pandas_ta as ta
from datetime import datetime, timedelta
import pandas as pd

api = TFU_Class2c.api

# Input variables
exchangeName = "NFO"
symbol = ""
buy_or_sell = ""
quantity = 50

app = Flask(__name__)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')

# Get LTP (Last Traded Price)
def getLTP(symbol):
    try:
        print("Inside getLtp")
        print("Exchange: " + exchangeName + ", Token: " + symbol)
        ret = api.get_quotes(exchange=exchangeName, token=symbol)
        return float(ret['lp'])
    except Exception as e:
        print(symbol, "Failed: {}".format(e))

# Place an order on Shoonya
def placeOrderShoonya(symbol, buy_or_sell, quantity, price):
    exchangeName = "NFO"
    print("Exchange: " + exchangeName + ", Symbol: " + symbol + ", Buy/Sell: " + buy_or_sell + ", Quantity: " + str(quantity) + ", Price: " + str(price))

    amo = "regular"
    order_type = "MARKET"
    symb = symbol
    paperTrading = 0

    if buy_or_sell == "BUY":
        buy_or_sell = "B"
    else:
        buy_or_sell = "S"

    if order_type == "MARKET":
        order_type = "MKT"
    elif order_type == "LIMIT":
        order_type = "L"
    else:
        order_type = "L"

    try:
        if paperTrading == 0:
            order_id = api.place_order(buy_or_sell=buy_or_sell,
                                       product_type="I",
                                       exchange=exchangeName,
                                       tradingsymbol=symb,
                                       quantity=quantity,
                                       discloseqty=quantity,
                                       price_type=order_type,
                                       price=price,
                                       trigger_price=price,
                                       amo=amo,
                                       retention="DAY")
            print(" => ", symb, order_id['norenordno'])
            return order_id['norenordno']
        else:
            order_id = 0
            return order_id
    except Exception as e:
        print("Failed to place order:", e)

# Get historical data
def get_time_series(exchange, token, days, interval):
    # Get the current date and time
    now = datetime.now()

    # Set the time to midnight
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Subtract days
    prev_day = now - timedelta(days=days)

    # Get the timestamp for the previous day
    prev_day_timestamp = prev_day.timestamp()

    # Use the prev_day_timestamp in your API call
    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=prev_day_timestamp, interval=interval)
    if ret:
        return pd.DataFrame(ret)
    else:
        print("No data for the given exchange, token, days, and interval")

# Fetch OHLC data and calculate Supertrend
# Fetch OHLC data and calculate Supertrend
def get_data(exchange, token, days, interval, ATR, Multi):
    # Get the time series data
    df = get_time_series(exchange, token, days, interval)
    df = df.sort_index(ascending=False)
    df[['into', 'intl', 'intc', 'inth', 'v']] = df[['into', 'intl', 'intc', 'inth', 'v']].apply(pd.to_numeric)

    # Calculate ATR
    high_low = df['inth'] - df['intl']
    high_close = np.abs(df['inth'] - df['intc'].shift())
    low_close = np.abs(df['intl'] - df['intc'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).sum() / 14

    # Calculate OBV (On Balance Volume)
    close = df['intc']
    volume = df['v']
    price_change = close.diff()
    obv = pd.Series(0, index=close.index)
    obv[1:] = (price_change[1:] > 0) * volume[1:] - (price_change[1:] < 0) * volume[1:]
    obv = obv.cumsum()

    # SuperTrend 007 calculation
    st_mult = 2
    st_period = 18
    factor = 0.4
    window_len = 10
    v_len = 14

    hilow = ((df['inth'] - df['intl']) * 100)
    openclose = ((df['intc'] - df['into']) * 100)
    vol = obv / hilow
    spreadvol = openclose * vol
    VPT = spreadvol + spreadvol.cumsum()

    price_spread = (df['inth'] - df['intl']).rolling(window_len).std()
    vx = spreadvol + spreadvol.cumsum()
    smooth = vx.ewm(span=v_len).mean()
    v_spread = (vx - smooth).rolling(window_len).std()
    shadow = (vx - smooth) / v_spread * price_spread
    out = np.where(shadow > 0, df['inth'] + shadow, df['intl'] + shadow)
    up_lev = out - (st_mult * atr)
    dn_lev = out + (st_mult * atr)
    Volatility = 100 * ((atr / df['intl']).rolling(1).sum()) / 100
    perc = (Volatility * 0.01) * factor
    hb = 0.00
    hl = 0.000
    lb = 0.00
    l1 = 0.000
    c = 0
    trend = 0
    n = dn_lev
    x = up_lev

    if True:
        c = 0
        lb = n
        hb = x
        l1 = out
        hl = out

    if c == 1:
        if x >= hb[1]:
            hb = x
            hl = out
            trend = 1
        else:
            lb = n
            l1 = out
            trend = -1

    if c > 1:
        if trend[1] > 0:
            hl = np.maximum(hl[1], out)
            if x >= hb[1]:
                hb = x
            else:
                if n < hb[1] - hb[1] * perc:
                    lb = n
                    l1 = out
                    trend = -1
        else:
            l1 = np.minimum(l1[1], out)
            if n <= lb[1]:
                lb = n
            else:
                if x > lb[1] + lb[1] * perc:
                    hb = x
                    hl = out
                    trend = 1

    # Calculate buy and sell signals
    trend_shifted = np.roll(trend, 1)  # Shift the trend array by 1 position
    buy_signals = np.where((trend == 1) & (trend_shifted == -1))[0]
    sell_signals = np.where((trend == -1) & (trend_shifted == 1))[0]

    # Place buy orders
    for buy_signal in buy_signals:
        print("Buy signal at index", buy_signal)
        price = df['intc'].iloc[buy_signal]  # Use the closing price at the buy signal index
        placeOrderShoonya(symbol, "BUY", quantity, price)

    # Place sell orders
    for sell_signal in sell_signals:
        print("Sell signal at index", sell_signal)
        price = df['intc'].iloc[sell_signal]  # Use the closing price at the sell signal index
        placeOrderShoonya(symbol, "SELL", quantity, price)

while True:
    get_data('NSE', '26000', 3, 15, 10, 3)
