import numpy as np
import pandas as pd
import talib

def supertrend_007(high, low, close, obv):
    st_mult = 2
    st_period = 18
    factor = 0.4

    hilow = ((high - low) * 100)
    openclose = ((close - close.shift()) * 100)
    vol = (obv / hilow)
    spreadvol = (openclose * vol)
    VPT = spreadvol + spreadvol.cumsum()

    window_len = 10
    v_len = 14
    price_spread = talib.STDDEV(high - low, window_len)
    vx = spreadvol + spreadvol.cumsum()
    smooth = talib.EMA(vx, v_len)
    v_spread = talib.STDDEV(vx - smooth, window_len)
    shadow = (vx - smooth) / v_spread * price_spread
    out = np.where(shadow > 0, high + shadow, low + shadow)

    atr = talib.ATR(high, low, close, st_period)
    up_lev = out - (st_mult * atr)
    dn_lev = out + (st_mult * atr)
    Volatility = 100 * talib.SUM(100 * talib.ATR(high, low, close, 1) / low, 1) / 100
    perc = (Volatility * 0.01) * factor

    hb = np.zeros_like(high)
    hb[1:] = np.nan_to_num(hb[:-1])
    hl = np.zeros_like(high)
    hl[1:] = np.nan_to_num(hl[:-1])
    lb = np.zeros_like(high)
    lb[1:] = np.nan_to_num(lb[:-1])
    l1 = np.zeros_like(high)
    l1[1:] = np.nan_to_num(l1[:-1])

    c = np.zeros_like(high)
    c[1:] = np.nan_to_num(c[:-1]) + 1
    trend = np.zeros_like(high)
    trend[1:] = np.nan_to_num(trend[:-1])

    for i in range(1, len(high)):
        if i == 1:
            c[i] = 0
            lb[i] = dn_lev[i]
            hb[i] = up_lev[i]
            l1[i] = out[i]
            hl[i] = out[i]
        
        if c[i] == 1:
            if up_lev[i] >= hb[i-1]:
                hb[i] = up_lev[i]
                hl[i] = out[i]
                trend[i] = 1
            else:
                lb[i] = dn_lev[i]
                l1[i] = out[i]
                trend[i] = -1

        if c[i] > 1:
            if trend[i-1] > 0:
                hl[i] = max(hl[i-1], out[i])
                if up_lev[i] >= hb[i-1]:
                    hb[i] = up_lev[i]
                else:
                    if dn_lev[i] < hb[i-1] - hb[i-1] * perc[i]:
                        lb[i] = dn_lev[i]
                        l1[i] = out[i]
                        trend[i] = -1
            else:
                l1[i] = min(l1[i-1], out[i])
                if dn_lev[i] <= lb[i-1]:
                    lb[i] = dn_lev[i]
                else:
                    if up_lev[i] > lb[i-1] + lb[i-1] * perc[i]:
                        hb[i] = up_lev[i]
                        hl[i] = out[i]
                        trend[i] = 1

    v = np.where(trend == 1, hb, np.where(trend == -1, lb, np.nan))

    buy_signals = np.where((trend == 1) & (trend.shift() == -1))[0]
    sell_signals = np.where((trend == -1) & (trend.shift() == 1))[0]

    for buy_signal in buy_signals:
        print("Buy signal at index", buy_signal)

    for sell_signal in sell_signals:
        print("Sell signal at index", sell_signal)

# Example usage
high = pd.Series([10, 12, 11, 13, 14])
low = pd.Series([8, 9, 10, 9, 10])
close = pd.Series([9, 11, 10, 12, 13])
obv = pd.Series([1000, 1200, 1100, 1300, 1400])

supertrend_007(high, low, close, obv)
