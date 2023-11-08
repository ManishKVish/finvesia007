from datetime import datetime, timedelta
import pandas as pd

def get_time_series(exchange, token, days, interval):
    # Get the current date and time
    now = datetime.now()

    # Set the time to midnight
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Subtract days
    prev_day = now - timedelta(days=days)

    # Get the timestamp for the previous day
    prev_day_timestamp = prev_day.timestamp()

    # Use the prev_day_timestamp in your api call
    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=prev_day_timestamp, interval=interval)
    if ret:
        return pd.DataFrame(ret)
    else:
        print("No Data for the given exchange, token, days and interval")
import pandas_ta as ta
import numpy as np
def supertrend(exchange, token, days, interval, ATR, Multi):
    # Get the time series data
    df = get_time_series(exchange, token, days, interval)
    df = df.sort_index(ascending=False)
    df[['into','intl','intc','inth']] = df[['into','intl','intc','inth']].apply(pd.to_numeric)
    #df[['into','intl','intc','inth']]
    sti = ta.supertrend(df['inth'], df['intl'], df['intc'], length=ATR, multiplier=Multi)
    sti = sti.sort_index(ascending=True)
    #sti[['SUPERT_10_3.0','SUPERTd_10_3.0']]    
    # Calculate the SuperTrend
    sti['super_trend'] = sti[['SUPERT_10_3.0']]
    result = pd.concat([df, sti], axis=1)
    results = result.sort_index(ascending=True).rename(columns={'SUPERTd_10_3.0': 'signal', 'SUPERTl_10_3.0': 'S_UPT','SUPERTs_10_3.0': 'S_DT'})
    results[['into','inth','intl','intc','SUPERT_10_3.0','signal']]=results[['into','inth','intl','intc','SUPERT_10_3.0','signal']].apply(pd.to_numeric)
    return results[['time','into','inth','intl','intc','signal','SUPERT_10_3.0','S_UPT','S_DT']]
import matplotlib.pyplot as plt

# Load your data into a pandas DataFrame
df = supertrend('NSE', '26000', 3, 15, 10, 3)
df = df.set_index('time')
df = df.sort_index(ascending=True)



# visualization
plt.plot(df['intc'],'k', label='Close Price')
plt.plot(df['S_UPT'], 'g', label = 'Final Lowerband')
plt.plot(df['S_DT'], 'r', label = 'Final Upperband')
plt.show()
df  = supertrend('NSE', '26000', 5, 5, 10, 3)
df
import pandas as pd
import math

def backtest_supertrend(df, investment):
    # Initialize variables
    in_position = False
    equity = investment
    commission = 1
    share = 0
    entry = []
    exit = []
    close = df['intc']
    signal = df['signal']
    time = df['time']
    # Loop through dataframe
    for i in range(len(df)):
        # If not in position & signal is 1 -> buy
        if not in_position and signal[i] == 1:
            share = equity / close[i]
            if share > 0:
                share = round(share,0)
                equity -= share * close[i]
                entry.append((time[i], close[i]))
                in_position = True
                print(f'Buy {int(share)} shares at {round(close[i],2)} on {time[i]}')
            else:
                print("Can not buy shares")
        # If in position & signal is -1 -> sell
        elif in_position and signal[i] == -1:
            equity += share * close[i] - commission
            exit.append((time[i], close[i]))
            in_position = False
            print(f'Sell {int(share)} shares at {round(close[i],2)} on {time[i]}')
    # If still in position -> sell all share 
    if in_position:
        equity += share * close[i] - commission
    earning = equity - investment
    roi = round(earning/investment*100,2)
    print(f'Earning from investing 100k is {round(earning,2)} (ROI = {roi}%)')
    return entry, exit, equity
df = supertrend('NSE', '26000', 100, 3, 10, 3)

df = df.sort_index(ascending=False)


entry, exit, roi = backtest_supertrend(df, 100000)