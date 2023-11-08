#!/usr/bin/env python
# coding: utf-8



import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c #Same filename of your login python file
import tkinter as tk
import pyotp



class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')


#credentials
api = ShoonyaApiPy()
user    = 'FA96867'
pwd     = 'Qwer@123'
totp = pyotp.TOTP('L2PJ4D67ZD77A5634L2J4KV3YR64U7S3')
# L2PJ4D67ZD77A5634L2J4KV3YR64U7S3
factor2 = totp.now()  #This should be TOTP
vc      = 'FA96867_U'
app_key = '70b40e0ac3f9823afdd648d2d0bbdd06'
imei    = 'abc1234'

accesstoken = 'e0eb3f0b151a8eff11574df3c51b8ab0bfee26aedba30c9b74207a6998196e7c'

#make the api call
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)

ret['stat']


api.searchscrip(exchange='MCX', searchtext='SILVERMIC')

api.searchscrip(exchange='MCX', searchtext='CRUDEOIL')



feed_opened = False
feedJson = {}
def event_handler_feed_update(tick_data):
     if 'lp' in tick_data and 'tk' in tick_data :
        timest = datetime.fromtimestamp(int(tick_data['ft'])).isoformat()
        feedJson[tick_data['tk']] = {'ltp': float(tick_data['lp']) , 'tt': timest}
    
def event_handler_order_update(tick_data):
    print(f"Order update {tick_data}")

def open_callback():
    global feed_opened
    feed_opened = True


api.start_websocket( order_update_callback=event_handler_order_update,
                     subscribe_callback=event_handler_feed_update, 
                     socket_open_callback=open_callback)

while(feed_opened==False):
    pass



#subscribe to multiple tokens
api.subscribe(['NSE|3045', 'NSE|11630'])



feedJson


while True:
    if feedJson['11630']['ltp'] > 7872:
        print('Target REached ')
        break






