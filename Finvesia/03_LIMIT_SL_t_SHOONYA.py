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

my_information = {  'NSE:TCS-EQ':   'NSE|11536',
                    'NFO:NIFTY09MAR23C17700':   'NFO|47223',
                    'NFO:NIFTY09MAR23C17600':   'NFO|47197',
                    'NFO:NIFTY09MAR23P17200':   'NFO|47102',
                    'NFO:NIFTY09MAR23P17300':   'NFO|47116'}

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


# List of available stocks
stock_list = ['NIFTY09MAR23C17700','NIFTY09MAR23C17600','NIFTY09MAR23P17200','NIFTY09MAR23P17300']


# Input variable
exchangeName = "NFO"
stockName = ""
buy_or_sell = ""
quantity = 50
target =2
stoploss =5
trailing = 1


# Function to get the user inputs from the GUI
def getUserInputs():
    global stockName
    global quantity
    global stoploss
    global trailing
    global target
    global limit_or_ltp
    global buy_or_sell
    stockName = selected_stock.get()
    quantity_str = quantity_entry.get()
    if quantity_str:
        quantity = int(quantity_str)
    else:
        quantity = 50

    target_str = target_entry.get()
    if target_str:
        target = float(target_str)

    else:
        target = 2

    stoploss_str = stoploss_entry.get()
    if stoploss_str:
        stoploss = float(stoploss_str)

    else:
        stoploss = 3

    trailing_str = trailing_entry.get()
    if trailing_str:
        trailing = float(trailing_str)
    else:
        trailing = 1

    if buy_var.get() == 0:
        buy_or_sell = "BUY"
    else:
        buy_or_sell = "SELL"



    limit_price_str = limit_price_entry.get()
    if limit_price_str:
        limit_or_ltp = float(limit_price_str)
        order_type1 = "LIMIT"
    else:
        limit_or_ltp = getLTP(stockName)
        order_type1 = "MARKET"

    print("stockname "+ stockName+" buy_or_sell "+buy_or_sell +"quantity "+str(quantity)+"target "+str(target)+"stoploss"+str(stoploss)+"traling"+str(trailing)+" LTP  "+ str(limit_or_ltp)+" order type "+order_type1)
    root.destroy()
    # Call the main function with the user inputs
    main(stockName, limit_or_ltp,quantity, buy_or_sell, target, stoploss, trailing, order_type1)



def exit_target(StockName, target_price,ltp):
    """
    Exit the position if the target price is reached
    """
    ltp = getLTP(StockName)
    if ltp >= target_price:
        print(f"Exit position {StockName} at {ltp} (Target price: {target_price})")
        return True
    return False

def exit_stoploss(StockName, stoploss_price,ltp):
    """
    Exit the position if the stop loss price is reached
    """
    ltp = getLTP(StockName)
    if ltp <= stoploss_price:
        print(f"Exit position {StockName} at {ltp} (Stop loss price: {stoploss_price})")
        return True
    return False

def exit_trailing_stoploss(StockName, entry_price, trail_amount):
    """
    Exit the position if the price falls below the trailing stop loss price
    """
    ltp = getLTP(StockName)
    trail_price = entry_price - trail_amount
    if ltp <= trail_price:
        print(f"Exit position {StockName} at {ltp} (Trailing stop loss price: {trail_price})")
        return True
    return False


def placeOrderShoonyaMarket(stockName, buy_or_sell, quantity, price):
    print("stockname "+ stockName+" buy_or_sell "+buy_or_sell +"quantity "+str(quantity)+"price "+str(price))

 
    order_type="MARKET"
    amo = "regular"
    symb = stockName
    price = 0
    
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
# Pass target and trailing stop loss to the API
        print(" => ", symb, order_id['norenordno'])
        return order_id['norenordno']
    except Exception as e:
     print("Failed to place order: ", e)

########################################################
# 
########################################################


# FOR PLACING LIMIT ORDER
def placeOrderShoonyaLimit(stockName, buy_or_sell, quantity, price):
    order_type="LMT"
    amo = "regular"
    symb = stockName
    
    if buy_or_sell == "BUY":
        buy_or_sell = "B"
    else:
        buy_or_sell = "S"

    print(" buy_or_sell "+buy_or_sell +"quantity "+str(quantity)+"exchange "
          + exchangeName + "tradingsymbol "+ symb +
            " price_type " +order_type + " price "
           + str(price) +" amo  "+amo ) 
    try: 
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
# Pass target and trailing stop loss to the API
        print(" => ", symb, order_id['norenordno'])

        return order_id['norenordno']
    except Exception as e:
     print("Failed to place order: ", e)


def get_status_of_order(orderNo):
   # norenordno = "23022500005682"
    while True:
        api =TFU_Class2c.api
        a = api.get_order_book()
        orderbook = pd.DataFrame(a)
        rejected_orders = orderbook.loc[ (orderbook["norenordno"] == str(orderNo))]
        # Iterate over the filtered orders and print their details
        for index, order in rejected_orders.iterrows():
            print("status:", order["status"])
            if order["status"] == "COMPLETE":
               print("order complete "+ order["status"]+ "price "+ order["avgprc"])
               return order["avgprc"]
            if order["status"] == "REJECTED":
               print(Fore.RED + "ORFER HAS BEEN REJECTED PLZ ADD NEW ORDER" + Style.RESET_ALL)
               return -1
               
        time.sleep(0.1)  # Wait for 1 second before checking again
      # Exit the loop if no successful order is found after waiting


# Create the GUI window
root = tk.Tk()
root.geometry('400x800')
root.title('NIFTY OPTIONS BUY AND SELL ')


# Create the stock name input fie
# 
# 
# ld and label
stockName_label = tk.Label(root, text='Stock Name:')
stockName_label.pack()



# market or limit order
# Initialize variables
order_type_var = tk.IntVar()
order_type_var.set(0) # set default value to 0, which means "MARKET" order


# Create a variable to hold the selected stock name
selected_stock = tk.StringVar()

# Create the dropdown menu with the stock list as options
stock_dropdown = tk.OptionMenu(root, selected_stock, *stock_list)
stock_dropdown.pack()

# Create the buy/sell radio buttons and label
buy_sell_label = tk.Label(root, text='Buy or Sell?')
buy_sell_label.pack()

# Create a BooleanVar to hold the value of whether the user wants to buy or sell
buy_var = tk.BooleanVar()
# Create the radio buttons for buying and selling
buy_radio = tk.Radiobutton(root, text='Buy', variable=buy_var, value=0)
sell_radio = tk.Radiobutton(root, text='Sell', variable=buy_var, value=1)
buy_radio.pack()
sell_radio.pack()


# Create the quantity input field and label
limit_price_label = tk.Label(root, text='LIMIT PRICE')
limit_price_label.pack()
limit_price_entry = tk.Entry(root, width=30)
limit_price_entry.pack()



# Create the quantity input field and label
quantity_label = tk.Label(root, text='QUANTITY :  (default: 50)')
quantity_label.pack()
quantity_entry = tk.Entry(root, width=30)
quantity_entry.pack()

# Create the target input field and label
target_label = tk.Label(root, text='TARGET :       (default: 2)')
target_label.pack()
target_entry = tk.Entry(root, width=30)
target_entry.pack()

# Create the stoploss input field and label

# Create the stop-loss slider and label
stoploss_label = tk.Label(root, text='STOP LOSS :        (default 3)')
stoploss_label.pack()
stoploss_entry = tk.Entry(root, width=30)
stoploss_entry.pack()


# Create the trailing input field and label
trailing_label = tk.Label(root, text='TRAILING STOPLOSS :     (default 1)')
trailing_label.pack()
trailing_entry = tk.Entry(root, width=30)
trailing_entry.pack()


# Create the submit button
submit_button = tk.Button(root, text='Submit', command=getUserInputs)
submit_button.pack()


# Modify the placeOrderShoonya function to accept target stop loss and trailing stop loss as inputs
def main(stockName, ltp ,quantity, buy_or_sell,target, stoploss, trailing, order_type1):
       # if we enter limit price calculation should use limit price other wise 
    # it should ltp
    if order_type1=="LIMIT":
            order_id = placeOrderShoonyaLimit(stockName, buy_or_sell, quantity, ltp)
            print(" limit price order  excute  "+ str(ltp))
            print(" order_id"+ str(order_id))
    else:
            order_id = placeOrderShoonyaMarket(stockName, buy_or_sell, quantity, ltp)
            print(" ltp order"+ str(ltp))
            print(" order_id"+ str(order_id))

    #until status is not successfull dont place the trade
    if order_type1=="LIMIT":
        ltp=float(get_status_of_order(order_id))
    
    #if it -1 means order has been rejected
    if ltp==-1:
        sys.exit(0)
        

    
    # Set initial target and stop loss prices
    target_price = ltp + target
    stoploss_price = ltp - stoploss
  
    print(stockName +"==> "+str(ltp)  +"target "+str(target_price)+" stoploss "+str(stoploss_price))
    while True:
        if order_id:
       # i want to take entry only
       # print(stockName +"==> "+str(ltp)  +"target "+str(target_price)+" stoploss "+str(stoploss_price) +"  trailing "+str(trail_price))
            ltp = getLTP(stockName)    
            # Check exit conditions
            if exit_target(stockName, target_price,ltp):
                # Place opposite order to close position
                opposite_direction = "SELL" if buy_or_sell == "BUY" else "BUY"
                placeOrderShoonyaMarket(stockName, opposite_direction, quantity, ltp)
                print(" target is hit at price "+ str(ltp))
                break
            
            if exit_stoploss(stockName, stoploss_price,ltp):
                # Place opposite order to close position
                opposite_direction = "SELL" if buy_or_sell == "BUY" else "BUY"
                placeOrderShoonyaMarket(stockName, opposite_direction, quantity, ltp)
                print(Fore.RED + " stoploss is hit at price "+ str(ltp) + Style.RESET_ALL)
                break
        else:
            break
        print(Fore.RED + stockName +"==> "+str(ltp)  +" TARGET :: "+str(target_price)+" STOPLOSS :: "+str(stoploss_price) + Style.RESET_ALL)

root.mainloop()
# Call the main function with the user inputs

