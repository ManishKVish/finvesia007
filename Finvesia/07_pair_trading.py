import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c #Same filename of your login python file
import tkinter as tk
import sys
from colorama import Fore, Style
import requests
import ta
import pandas as pd



class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')
api =TFU_Class2c.api

#####################################################################################################

# Download stock data for two stocks for last 21 candle on 5 min chart
today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)
yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

def get_close_candle_data_for_interval(exchange, token, starttime,interval):
    #GAL 4717
    #ONGC 2475
    stockData= api.get_time_price_series(exchange, token, starttime, interval)
    # Get the last 21 close candles
    last_candles = stockData[-21:]
    # Extract the close values
    close_values = [candle["intc"] for candle in last_candles]
    # Print the close values
    print(close_values)
    return close_values

stock1 = get_close_candle_data_for_interval(exchange='NSE', token='4717', starttime=yesterday.timestamp(), interval=5)
stock2 = get_close_candle_data_for_interval(exchange='NSE', token='2475', starttime=yesterday.timestamp(), interval=5)


# Compute the price ratio of the two stocks
price_ratio =  stock1/ stock2

print(price_ratio)

# Compute the z-score of the price ratio
length = 21
std_devs = 2.0
basis = ta.trend.sma(price_ratio, window=length)
zscore = (price_ratio - basis) / ta.volatility.stdev(price_ratio, window=length)

# Set up alert conditions for entering and exiting trades
if zscore[-1] > 2:
    print("SELL 1 - BUY 2")
elif zscore[-1] < -2:
    print("BUY 1 - SELL 2")
