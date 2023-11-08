import requests
import time
from NorenRestApiPy.NorenApi import NorenApi
from flask import Flask, request
import TFU_Class2c  # Same filename of your login python file
import pandas as pd

app = Flask(__name__)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')
        
api = TFU_Class2c.api

my_information = {  'NSE:TCS-EQ':   'NSE|11536',
                    'NFO:NIFTY01JUN23P18300':   'NFO|50456',
                    'NFO:NIFTY01JUN23C18800':   'NFO|50477',
                       "NSE:NIFTY": "NSE|26000",
                        "NSE:BANKNIFTY": "NSE|26009"
  }

def getLTP(token):
    exch='NFO'
    instrument = exch+":"+token
    instrument = my_information[instrument]
    url = "http://localhost:4002/ltp?instrument=" + instrument
    resp = None
    try:
        resp = requests.get(url)
    except Exception as e:
        print(e)
    if resp is not None:
        data = resp.json()
        return data
    else:
        return None


def get_position():
    #print(api.get_holdings())
    print("---------------")
    print(api.subscribe_orders())
    print(api.get_order_book())


def main():
   while True:
    get_position()

    # while True:
    #     stockName= "NIFTY01JUN23P18300"
    #     k = getLTP(stockName)
    #     if k is not None:
    #         print(stockName  ,k)
    #     time.sleep(2)


main()
