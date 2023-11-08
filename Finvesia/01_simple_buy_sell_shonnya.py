

import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c #Same filename of your login python file
import tkinter as tk

api =TFU_Class2c.api

# Input variable
exchangeName = "NFO"
stockName = ""
buy_or_sell = ""
quantity = 50

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')

# Function to get the last traded price
def getLTP(stockName):
    try:
        print(" inside getLtp")
        print("exch : "+ exchangeName+ " token : "+ stockName)
        ret = api.get_quotes(exchange=exchangeName, token=stockName)
        return float(ret['lp'])
    except Exception as e:
        print(stockName , "Failed : {} ".format(e))

# Function to place an order
def placeOrderShoonya(stockName, buy_or_sell, quantity, price):
    amo = "regular"
    order_type = "MARKET"
    symb = stockName
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
        print("Failed to place order: ", e)

# Function to get the user inputs from the GUI
def getUserInputs():
    global stockName
    global quantity

    # Call the main function with the user inputs
    ltp = getLTP(stockName)
    print(stockName +"==> "+str(ltp))
    order_id = placeOrderShoonya(stockName, buy_or_sell, quantity, ltp)
    print(order_id)
    time.sleep(2)


# Call the main function with the user inputs

