import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c #Same filename of your login python file
import tkinter as tk

api =TFU_Class2c.api

a = api.get_order_book()
orderbook = pd.DataFrame(a)

# Specify the filename and path where you want to save the CSV file
filename = 'orderbook.csv'

# Save the dataframe as a CSV file
orderbook.to_csv(filename, index=False)

print("Orderbook data saved as CSV file:", filename)

# Filter out orders with status "REJECTED" and norenordno equal to a specific value
norenordno = "23022500005682"
rejected_orders = orderbook.loc[(orderbook["status"] == "REJECTED") & (orderbook["norenordno"] == norenordno)]

# Iterate over the filtered orders and print their details
for index, order in rejected_orders.iterrows():
    print("Order details:")
    print("---------------")
    print("norenordno:", order["stat"])
    print("exchange:", order["kidid"])
    print("price:", order["avgprc"])
    
    print("status:", order["status"])

    print("---------------")
