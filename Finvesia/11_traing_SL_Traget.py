
import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c #Same filename of your login python file
import tkinter as tk
import sys
import requests


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')

api =TFU_Class2c.api

target_price =100

my_information = {  'NSE:TCS-EQ':   'NSE|11536',
                    'NFO:NIFTY09MAR23C17700':   'NFO|47223',
                    'NFO:NIFTY09MAR23C17600':   'NFO|47197',
                    'NFO:NIFTY09MAR23P17200':   'NFO|47102',
                    'NFO:NIFTY09MAR23P17300':   'NFO|47116'}


def checkinng_target_sl_achived():
    ltp_data = getLTP('TCS-EQ')
    if ltp_data is not None:
        ltp = ltp_data.get('LTP')
        if ltp is not None:
            if ltp >= target_price:
                print("Target achieved!")
            else:
                print("Target not yet achieved.")
        else:
            print("Unable to fetch LTP.")
    else:
        print("Error in retrieving LTP data.")



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
    
getLTP('NSE:TCS-EQ')