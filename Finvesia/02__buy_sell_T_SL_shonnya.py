import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
import TFU_Class2c  # Same filename of your login python file
import tkinter as tk

api = TFU_Class2c.api

# List of available stocks
stock_list = ["NIFTY02MAR23P17300", "NIFTY02MAR23C17700"]


# Input variable
exchangeName = "NFO"
stockName = ""
buy_or_sell = ""
quantity = 50
target = 2
stoploss = 5
trailing = 1


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(
            self,
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
            eodhost="https://api.shoonya.com/chartApi/getdata/",
        )


# Function to get the last traded price
def getLTP(stockName):
    try:
        print(" inside getLtp")
        print("exch : " + exchangeName + " token : " + stockName)
        ret = api.get_quotes(exchange=exchangeName, token=stockName)
        return float(ret["lp"])
    except Exception as e:
        print(stockName, "Failed : {} ".format(e))


# Function to get the user inputs from the GUI
def getUserInputs():
    global stockName
    global quantity
    global stoploss
    global trailing
    global target
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

    if order_type_var.get() == 0:
        order_type = "MARKET"
        limit_price = None
    else:
        order_type = "LIMIT"
        limit_price_str = limit_price_entry.get()
        if limit_price_str:
            limit_price = float(limit_price_str)
        else:
            limit_price = None

    print(
        "stockname "
        + stockName
        + " buy_or_sell "
        + buy_or_sell
        + "quantity "
        + str(quantity)
        + "target "
        + str(target)
        + "stoploss"
        + str(stoploss)
        + "traling"
        + str(trailing)
        + "order_type "
        + order_type
        + "limit_price "
        + str(limit_price)
    )

    root.destroy()

    # Call the main function with the user inputs
    ltp = getLTP(stockName)
    print(stockName + "==> " + str(ltp))
    order_id = placeOrderShoonya(stockName, buy_or_sell, quantity, ltp)
    print(order_id)
    time.sleep(2)


def exit_target(StockName, target_price):
    """
    Exit the position if the target price is reached
    """
    ltp = getLTP(StockName)
    if ltp >= target_price:
        print(f"Exit position {StockName} at {ltp} (Target price: {target_price})")
        return True
    return False


def exit_stoploss(StockName, stoploss_price):
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
        print(
            f"Exit position {StockName} at {ltp} (Trailing stop loss price: {trail_price})"
        )
        return True
    return False


def placeOrderShoonya(stockName, buy_or_sell, quantity, price):
    print(
        "stockname "
        + stockName
        + " buy_or_sell "
        + buy_or_sell
        + "quantity "
        + str(quantity)
        + "price "
        + str(price)
    )

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
            order_id = api.place_order(
                buy_or_sell=buy_or_sell,
                product_type="I",
                exchange=exchangeName,
                tradingsymbol=symb,
                quantity=quantity,
                discloseqty=quantity,
                price_type=order_type,
                price=price,
                trigger_price=price,
                amo=amo,
                retention="DAY",
            )
            # Pass target and trailing stop loss to the API
            print(" => ", symb, order_id["norenordno"])
            return order_id["norenordno"]
        else:
            order_id = 0
            return order_id
    except Exception as e:
        print("Failed to place order: ", e)


# Create the GUI window
root = tk.Tk()
root.geometry("400x800")
root.title("NIFTY OPTIONS BUY AND SELL ")


# Create the stock name input field and label
stockName_label = tk.Label(root, text="Stock Name:")
stockName_label.pack()


# market or limit order
# Initialize variables
order_type_var = tk.IntVar()
order_type_var.set(0)  # set default value to 0, which means "MARKET" order
limit_price_entry = tk.Entry(root)


# Create a variable to hold the selected stock name
selected_stock = tk.StringVar()

# Create the dropdown menu with the stock list as options
stock_dropdown = tk.OptionMenu(root, selected_stock, *stock_list)
stock_dropdown.pack()

# Create the buy/sell radio buttons and label
buy_sell_label = tk.Label(root, text="Buy or Sell?")
buy_sell_label.pack()

# Create a BooleanVar to hold the value of whether the user wants to buy or sell
buy_var = tk.BooleanVar()
# Create the radio buttons for buying and selling
buy_radio = tk.Radiobutton(root, text="Buy", variable=buy_var, value=0)
sell_radio = tk.Radiobutton(root, text="Sell", variable=buy_var, value=1)
buy_radio.pack()
sell_radio.pack()

market_limit_lable = tk.Label(root, text="MARKET OR LIMIT ")
market_limit_lable.pack()
# Create a BooleanVar to hold the value of whether the user wants to buy or sell
market_limit_var = tk.BooleanVar()
# Create the radio buttons for buying and selling
market_radio = tk.Radiobutton(root, text="MARKET", variable=market_limit_var, value=0)
lilmit_radio = tk.Radiobutton(root, text="LIMIT", variable=market_limit_var, value=1)
market_radio.pack()
lilmit_radio.pack()


# Create the quantity input field and label
quantity_label = tk.Label(root, text="QUANTITY :  (default: 50)")
quantity_label.pack()
quantity_entry = tk.Entry(root, width=30)
quantity_entry.pack()

# Create the target input field and label
target_label = tk.Label(root, text="TARGET :       (default: 2)")
target_label.pack()
target_entry = tk.Entry(root, width=30)
target_entry.pack()

# Create the stoploss input field and label

# Create the stop-loss slider and label
stoploss_label = tk.Label(root, text="STOP LOSS :        (default 3)")
stoploss_label.pack()
stoploss_entry = tk.Entry(root, width=30)
stoploss_entry.pack()


# Create the trailing input field and label
trailing_label = tk.Label(root, text="TRAILING STOPLOSS :     (default 1)")
trailing_label.pack()
trailing_entry = tk.Entry(root, width=30)
trailing_entry.pack()


# Create the submit button
submit_button = tk.Button(root, text="Submit", command=getUserInputs)
submit_button.pack()


# Modify the placeOrderShoonya function to accept target stop loss and trailing stop loss as inputs
def main(stockName, quantity, target, stoploss, trailing):
    ltp = getLTP(stockName)

    order_id = placeOrderShoonya(stockName, buy_or_sell, quantity, ltp)
    print(order_id)

    # Set initial target and stop loss prices
    target_price = ltp + target
    stoploss_price = ltp - stoploss
    entry_price = ltp

    while True:
        print(
            stockName
            + "==> "
            + str(ltp)
            + "target "
            + str(target_price)
            + " stoploss "
            + str(stoploss_price)
            + "  trailing "
            + str(trail_price)
        )
        ltp = getLTP(stockName)
        print(stockName + "==> " + str(ltp))

        # Check exit conditions
        if exit_target(stockName, target_price):
            # Place opposite order to close position
            opposite_direction = "SELL" if buy_or_sell == "BUY" else "BUY"
            placeOrderShoonya(stockName, opposite_direction, quantity, ltp)
            break

        if exit_stoploss(stockName, stoploss_price):
            # Place opposite order to close position
            opposite_direction = "SELL" if buy_or_sell == "BUY" else "BUY"
            placeOrderShoonya(stockName, opposite_direction, quantity, ltp)
            break

        if exit_trailing_stoploss(stockName, entry_price, trailing):
            # Place opposite order to close position
            opposite_direction = "SELL" if buy_or_sell == "BUY" else "BUY"
            placeOrderShoonya(stockName, opposite_direction, quantity, ltp)
            break

        # Update trailing stop loss price
        trail_price = entry_price - trailing
        if ltp > entry_price:
            entry_price = ltp
            trail_price = entry_price - trailing

        stoploss_price = max(stoploss_price, trail_price)

        # Update target price
        target_price = max(target_price, ltp + target)

        time.sleep(2)


root.mainloop()
# Call the main function with the user inputs
