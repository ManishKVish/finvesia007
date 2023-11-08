import datetime

import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi

import TFU_Class2c #Same filename of your login python file
from colorama import Fore, Style
import numpy as np
import pandas as pd

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')

api =TFU_Class2c.api

my_information = {  'NSE:TCS-EQ':   'NSE|11536',
                    'NFO:NIFTY09MAR23C17700':   'NFO|47223',
                    'NFO:NIFTY09MAR23C17600':   'NFO|47197',
                    'NFO:NIFTY09MAR23P17200':   'NFO|47102',
                    'NFO:NIFTY09MAR23P17300':   'NFO|47116'}

#####################################################################################################

# Download stock data for two stocks for last 21 candle on 5 min chart

today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)
yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
#GAL 4717
#ONGC 2475

stock1 = api.get_time_price_series(exchange='NSE', token='4717', starttime=yesterday.timestamp(), interval=15)
# Get the last 14 close candles
last_14_candles1 = stock1[-21:]
# Extract the close values
close_values1 = [float(candle["intc"]) for candle in last_14_candles1]


stock2 = api.get_time_price_series(exchange='NSE', token='2475', starttime=yesterday.timestamp(), interval=15)
# Get the last 14 close candles
last_14_candles2 = stock2[-21:]
# Extract the close values
close_values2 = [float(candle["intc"]) for candle in last_14_candles2]



# Print the close values
print(close_values1)
print(close_values2)

# Compute the price ratio of the two stocks
price_ratio = []
for i in range(len(close_values1)):
    print(str(close_values1[i]) +"   " + str(close_values2[i]))
    price_ratio.append(close_values1[i] / close_values2[i])


print(price_ratio)

###########################################################################################
# Compute the z-score of the price ratio
from scipy.stats import zscore


# Calculate the z-score of the data
z_scores = zscore(price_ratio)

# Print the z-score of each data point
print(z_scores)

