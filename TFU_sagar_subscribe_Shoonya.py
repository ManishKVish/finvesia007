import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#from api_helper import ShoonyaApiPy
import TFU_Class2c
from pprint import pprint
import datetime
import logging
import time
import yaml
import pandas as pd
from time import sleep
import pyotp
import threading
from flask import Flask, request

##############################################
#                   INPUT's                  #
##############################################
# NSE:ACC   --> NSE|22
# NSE:NTPC  --> NSE|11630
instrumentList = [
    'NSE|26000', # NIFTY 50 SPOT
    'NSE|26009' # BANK NIFTY SPOT
]

##############################################
#                   SERVER                   #
##############################################
app = Flask(__name__)
LTPDICT = {}

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/test')
def test():
    return LTPDICT

@app.route('/ltp')
def getLtp():
    global LTPDICT
    try:
        print(LTPDICT)
        ltp = -1
        instrumet = request.args.get('instrument')
        ltp = LTPDICT[instrumet]
    except Exception as e :
        print("EXCEPTION occured while getting LTPDICT()")
        print(e)
    return str(ltp)


def startServer():
    print("Inside startServer()")
    app.run(host='0.0.0.0', port=4002)

##############################################
#                  SHOONYA                   #
##############################################

socket_opened = False
api = TFU_Class2c.api

# # For debugging enable this
#logging.basicConfig(level=logging.DEBUG)

#application callbacks
def event_handler_order_update(message):
    print("ORDER : {0}".format(time.strftime('%d-%m-%Y %H:%M:%S')) + str(message))

def event_handler_quote_update(tick):
    global LTPDICT
    key = tick['e'] + '|' + tick['tk']
    LTPDICT[key] = tick['lp']
    print(LTPDICT)

def open_callback():
    global socket_opened
    socket_opened = True
    print('app is connected')

    # api.subscribe('NSE|11630', feed_type='d')
    api.subscribe(instrumentList)

#end of callbacks

def get_time(time_string):
    data = time.strptime(time_string,'%d-%m-%Y %H:%M:%S')
    return time.mktime(data)

def main():
    global uid
    global pwd
    global vc
    global app_key
    global imei

    #start of our program
    print(" Main Started ")
    t1 = threading.Thread(target=startServer)
    t1.start()
    sleep(1)

    ret = api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)

    sleep(2)
    while True:
        continue

    t1.join()


main()

