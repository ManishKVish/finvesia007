from NorenRestApiPy.NorenApi import NorenApi
from flask import Flask, request
import pyotp
import TFU_Class2c  # Same filename of your login python file
import pandas as pd
import re
import threading
from queue import Queue
import requests
import time
import datetime
import traceback

app = Flask(__name__)


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
                   #       eodhost='https://api.shoonya.com/chartApi/getdata/')
        global api
        api = self
#enable dbug to see request and responses
#logging.basicConfig(level=logging.DEBUG)

def Shoonya_login():
    #credentials
    api = ShoonyaApiPy()
    user    = 'FA96867'
    pwd     = 'Qwer@0987'
    totp = pyotp.TOTP('L2PJ4D67ZD77A5634L2J4KV3YR64U7S3')
    # L2PJ4D67ZD77A5634L2J4KV3YR64U7S3
    factor2 = totp.now()  #This should be TOTP
    vc      = 'FA96867_U'
    app_key = '70b40e0ac3f9823afdd648d2d0bbdd06'
    imei    = 'abc1234'

   # accesstoken = 'e0eb3f0b151a8eff11574df3c51b8ab0bfee26aedba30c9b74207a6998196e7c'

    #make the api call
    ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
    print(ret)
    print(ret['susertoken'])
    print(api)


Shoonya_login()


api = ShoonyaApiPy()


# -VE      IN THE MONEY
# 0  ATM
# +VE     OUT THE MONEY

target_percent = 1.10
sl_percent = 0.90
otm = -100
default_quantiy = 100


fst_target_points = 0.12
Snd_target_points = 0.22
expiry = {
    "year": "23",
    "month": "NOV",
    "day": "09"
}
my_information = {
    "NSE:NIFTY": "NSE|26000",
    "NSE:BANKNIFTY": "NSE|26009",
}


# BUY SELL OR COMMENT FOR BOTH  BUY_SELL  BUY  SELL

buy_or_sell_flag = "C_BUY P_BUY"
fst_target_flag = False
Snd_target_flag =  False
previous_symbol = None
entry_price = None
previous_quantity = None
fst_target = None
fst_target_order_no = None
fst_target_ltp = None
Snd_target_ltp = None
closePrice = None
target_order_id = None
sl_order_id = None


stop_event = threading.Event()


target_loop = False
# quantity should be multiple of 100

last_postion = "HALF"
stock = "NIFTY"
# -VE      IN THE MONEY
# 0  ATM
# +VE     OUT THE MONEY

##################################################

def getLTP_websocket(exch, token):
    time.sleep(0.9)
    print(" getLTP_websocket() ")
    if exch == None:
        exch = "NFO"
    instrument = exch + ":" + token
    instrument = my_information[instrument]
    
    url = "http://localhost:4002/ltp?instrument=" + instrument
    resp = None
    try:
        resp = requests.get(url)
    except Exception as e:
        print(e)
    if resp != None:
        data = resp.json()
        # print("data"+ str(data))
        return data
    else:
        return getLTP(instrument)


def getLTP(symbol):
    print(" getLTP() ")
    try:
        print("inside getLtp")
        print("exch: NFO, token: " + symbol)
        ret = api.get_quotes(exchange="NFO", token=symbol)
        print("exch: NFO, token: " + symbol + " LTP IS " + str(float(ret["lp"])))
        return float(ret["lp"])
    except Exception as e:
        print(symbol, "INVALID SYMBOL : {}".format(e))


def findStrikePriceATM(type, stock):
    print(" findStrikePriceATM  ")
    global closePrice

    # TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"
    strikeList = []
    prev_diff = 10000
    closest_Strike = 10000
    intExpiry = expiry["day"] + expiry["month"] + expiry["year"]  # 22OCT
    ######################################################
    # FINDING ATM
    ltp = float(getLTP_websocket("NSE","NIFTY"))
    print("ltp :: "+ str(ltp))
    closePrice = ltp

    if stock == "BANKNIFTY":
        closest_Strike = int(round((ltp / 100), 0) * 100)
        print(closest_Strike)
    elif stock == "NIFTY":
        closest_Strike = int(round((ltp / 50), 0) * 50)
        print(closest_Strike)
    elif stock == "NIFTY1!":
        closest_Strike = int(round((ltp / 50), 0) * 50)
        print(closest_Strike)

    print("closest", closest_Strike)
    closest_Strike_CE = closest_Strike + otm
    closest_Strike_PE = closest_Strike - otm
    print(f"CE: {closest_Strike_CE} PE: {closest_Strike_PE}")

    if stock == "BANKNIFTY":
        atmCE = "BANKNIFTY" + str(intExpiry) + "C" + str(closest_Strike_CE)
        atmPE = "BANKNIFTY" + str(intExpiry) + "P" + str(closest_Strike_PE)
        
    elif stock == "NIFTY":
        atmCE = "NIFTY" + str(intExpiry) + "C" + str(closest_Strike_CE)
        atmPE = "NIFTY" + str(intExpiry) + "P" + str(closest_Strike_PE)
    
    # NIFTY! FOR FUT CHART
    elif stock == "NIFTY1!":
        atmCE = "NIFTY" + str(intExpiry) + "C" + str(closest_Strike_CE)
        atmPE = "NIFTY" + str(intExpiry) + "P" + str(closest_Strike_PE)

    if type == "C_BUY":
        return atmCE
    if type == "P_BUY":
        return atmPE


@app.route("/ob1", methods=["GET"])
def health():
    result = getLTP_websocket("NSE", "NIFTY")
    return str(result)

@app.route("/ob_reset", methods=["GET", "POST"])
def reset_variables():
    print("reset_variables ()")
    print("reseting all the variable ")
    global target_loop
    global fst_target_flag
    global Snd_target_flag
    global previous_symbol
    global entry_price
    global previous_quantity
    global fst_target
    global fst_target_order_no
    global fst_target_ltp
    global Snd_target_ltp
    global closePrice
    global target_order_id
    global sl_order_id
    
    if sl_order_id != None:
            api.cancel_order(sl_order_id)
    if target_order_id != None:
            api.cancel_order(target_order_id)

    # Assign default values to the variables
    target_loop = False
    fst_target_flag = False
    Snd_target_flag = False
    previous_symbol = None
    entry_price = None
    previous_quantity = None
    fst_target = None
    fst_target_order_no = None
    fst_target_ltp = None
    Snd_target_ltp = None
    closePrice = None
    target_order_id = None
    sl_order_id = None
    return "reset all the variable"

@app.route("/ob", methods=["GET", "POST"])
def receive_webhook():
    global previous_symbol, previous_message, previous_orderNo, closePrice
    alert_data = request.get_json()
    symbol = alert_data.get("symbol")
    message = alert_data.get("message")
    quantity = alert_data.get("quantity")
    interval = alert_data.get("interval")
    closePrice = alert_data.get("close")
    timenow = alert_data.get("timenow")


    # if already buy position is there it will not take buy position
    if previous_symbol is not None:
        if "P_BUY" in message and "23P" in previous_symbol:
            return "already buy position active"
        elif "C_BUY" in message and "23C" in previous_symbol:
            return "already Sell position active"
    
    if "P_EXIT" in message and "23P" in previous_symbol:
        exit_at_market()
    if "C_EXIT" in message and "23C" in previous_symbol:
        exit_at_market()
        

    variables = {
        "symbol": symbol,
        "message": message,
        "interval": interval,
        "closePrice": closePrice,
        "timenow": timenow,
    }
    none_variables = [name for name, value in variables.items() if value is None]

    if none_variables:
        none_variable_names = ", ".join(none_variables)
        print(f"The following variable(s) have a value of None: {none_variable_names}")
        # return f"The following variable(s) have a value of None: {none_variable_names}"

        # order is already there

    try:
        return get_exchange_Symbol_strikePrice_orderAreadyPlaced(symbol, message)
    except Exception as e:
        return "FAILED TO PLACE ORDER" + str(e)

def exit_at_market():
    print(" exit_at_market () ")
    global previous_symbol, previous_quantity, sl_order_id, target_order_id
    if previous_symbol != None:
        # if previous_quantity == default_quantiy:
        try:
            api.cancel_order(sl_order_id)
        except Exception as e:
            print(" NOT ABLE TO CANCEL STOPLOSS ORDER" + str(e))
        print("SELL ORDER WITH "+ previous_symbol+ " AND QUANTITY "+ str(previous_quantity))
        try:
            order_id = placeOrder(previous_symbol, "SELL", previous_quantity, 0, "MARKET")
        except Exception as e:
            print(" NOT ABLE TO EXIT AT THE TARGET" + str(e))
    reset_variables()
    return get_status_of_order(order_id)


def getToken(exch, symbol):
    try:
        output = api.searchscrip(exchange=exch, searchtext=symbol)
        return output["values"][0]["token"]
    except Exception as e:
        print(" NOT ABLE TO FIND TOKEN FOR SYMBOL" + str(e))

def get_exchange_Symbol_strikePrice_orderAreadyPlaced(symbol, message):
    print(" Create two threads for method1 and method2 ")
    global previous_message, previous_symbol, target_loop
    target_loop = False

    if sl_order_id != None:
            api.cancel_order(sl_order_id)
    if target_order_id != None:
            api.cancel_order(target_order_id)

    # Create two threads for method1 and method2
    string1 = None
    string2 = None
    try:
        # Create a result queue
        result_queue = Queue()

        def thread1_func():
            print("inside thread1_func")
            nonlocal string1
            try:
                string1 = exit_order(symbol, message)
                result_queue.put(string1)  # Put the result in the queue
            except Exception as e:
                print(f"Exception occurred in thread1_fun  SELL ORDERc: {e}")
                return f"Exception occurred in thread1_func SELL ORDER: {e}"
                # raise Exception(f" SELL ORDER : {e}")

        def thread2_func():
            print("inside thread2_func")
            nonlocal string2
            try:
                string2 = entry_order(symbol, message)
                result_queue.put(string2)  # Put the result in the queue
            except Exception as e:
                print(f"Exception occurred in thread2_func BUY ORDER: {e}")
                return f"Exception occurred in thread2_func BUY ORDER: {e}"
            # Create thread objects

        thread1 = threading.Thread(target=thread1_func)
        thread2 = threading.Thread(target=thread2_func)

        # Start both threads

        thread1.start()
        time.sleep(0.1)
        thread2.start()

        # Join both threads
        thread1.join()
        thread2.join()

        # Get the results from the queue
        # string1 = result_queue.get()
        # string2 = result_queue.get()
        print("-----BOTH THREAD COMPLETED-----")

    except Exception as e:
        print(f"Exception occurred: {e}")

    # Join the strings
    joined_string = ""
    if string1 != None and string2 != None:
        joined_string = string1 + string2

    return joined_string


# BUY C_BUY AND P_SELL
# SYMBOL NIFTY\ob

# SELL P_BUY AND C_SELL
# NIFTY01JUN23C19000
def exit_order(symbol, message):

    print(" exit_order () ")
    global previous_symbol, previous_quantity, sl_order_id, target_order_id
    # both have same stock name
    # previous symbol have C or not
    # new message have sell siganl or not
    if previous_symbol != None:
        # if previous_quantity == default_quantiy:
        #     api.cancel_order(fst_target_order_no)

        print(
            "SELL ORDER WITH "
            + previous_symbol
            + " AND QUANTITY "
            + str(previous_quantity)
        )
        if symbol in previous_symbol and "C" in previous_symbol and "C_SELL" in message:
            order_id = placeOrder(
                previous_symbol, "SELL", previous_quantity, 0, "MARKET"
            )
            return get_status_of_order(order_id)
        elif (
            symbol in previous_symbol and "P" in previous_symbol and "P_SELL" in message
        ):
            order_id = placeOrder(
                previous_symbol, "SELL", previous_quantity, 0, "MARKET"
            )
            return get_status_of_order(order_id)
    else:
        print("PREVIOUS TRADE != ACTIVE : NO SELL ORDER")
        return "PREVIOUS TRADE != ACTIVE : NO SELL ORDER"
    print("NOT ABLE TO EXIT QUANTITY")


# OPtions BUY order
def entry_order(symbol, message):
        print(" entry_order() ")
        global previous_symbol, previous_quantity, last_postion, fst_target, fst_target_order_no, target_loop, no_trade_time_start_hour, no_trade_time_start_min, no_trade_time_end_hour,no_trade_time_end_min,fst_target_ltp , Snd_target_ltp, fst_target_points, Snd_target_points,  closePrice
        if "C_BUY" in message:
            if "C_BUY" in buy_or_sell_flag:
                option_symbol = findStrikePriceATM("C_BUY", symbol)
                print(option_symbol)
                order_id = placeOrder(option_symbol, "BUY", default_quantiy, 0, "MARKET")
                string1 = get_status_of_order(order_id)
                if string1 == "COMPLETE":
                    print(" ASSIGN VALUE IN CE BUY ORDER ")
                    # if order id completed than only set the previous_symbol, previous symbol, entry_price
                    # entrypreice set from get_status_of_order
                    previous_symbol = option_symbol
                    previous_quantity = default_quantiy
                    add_stop_loss_limit()
                # i want to call a method which run in background check ltp is reaches to 1.1*entry_price it shold print exit half quantity
                return string1
            raise Exception("CE :: BUYING != THERE IN THE FLAG")
        if "P_BUY" in message:
            if "P_BUY" in buy_or_sell_flag:
                option_symbol = findStrikePriceATM("P_BUY", symbol)
                print(option_symbol)
                order_id = placeOrder(option_symbol, "BUY", default_quantiy, 0, "MARKET")
                string1 = get_status_of_order(order_id)
                if string1 == "COMPLETE":
                    print(" ASSIGN VALUE IN PE BUY ORDER ")
                    # if order id completed than only set the previous_symbol, previous symbol, entry_price
                    # entrypreice set from get_status_of_order
                    previous_symbol = option_symbol
                    previous_quantity = default_quantiy
                    last_postion = "FULL"
                   # calculating targe for CE 
                    target_loop = True
                    add_stop_loss_limit()
                return string1
            raise Exception("PE :: BUYING != THERE IN THE FLAG")
        else:
            print("OPTION SYMBOL NOT FOUND FOR THE GIVEN SYMBOL AND MESSAGE.")
            
def add_stop_loss_limit():
    global sl_order_id
    try:
        if sl_exit != None:
         sl_order_id = placeOrder(
            previous_symbol, "SELL", previous_quantity, sl_exit, "SL-LMT")
    except Exception as e:
        print(" NOT ABLE TO PLACE AND SL LIMIT ORDER ")

def get_status_of_order(orderNo):
    print(" get_status_of_order() ")
    global entry_price, fst_target, sl_exit, target_percent, sl_percent, target_order_id, sl_order_id, previous_symbol, previous_quantity
    a = api.get_order_book()
    orderbook = pd.DataFrame(a)
    rejected_orders = orderbook.loc[orderbook["norenordno"] == str(orderNo)]

    for index, order in rejected_orders.iterrows():
        print("status:", order["status"])
        if order["status"] == "COMPLETE":
            print("ORDER COMPLETE " + order["status"] + " price " + order["avgprc"])

            entry_price = float(order["avgprc"])
            entry_price = format(entry_price, ".1f")

            fst_target = float(target_percent) * float(order["avgprc"])
            fst_target = format(fst_target, ".1f")

            sl_exit = float(sl_percent) * float(order["avgprc"])
            sl_exit = format(sl_exit, ".1f")

            #################################

            # print("ENTRY PRICE :"+str(order["avgprc"] )+ " TARGET IS  :"+str(fst_target ) + " SL :"+ +str(sl_exit ))
            return order["status"]
        if order["status"] == "REJECTED":
            print("ORDER HAS BEEN REJECTED PLEASE ADD NEW ORDER")
            raise Exception("ORDER HAS BEEN REJECTED PLEASE ADD NEW ORDER")
    raise Exception(
        "RETURN NO ORDER IN THE ORDER-BOOK WITH ORDER NUMBER " + orderNo
    )  # Return None if the order != found in the order book


def placeOrder(symbol, buy_or_sell, quantity, price, order_type):
    global previous_symbol, previous_quantity, previous_orderNo
    print(
        "PLACE ORDER :: exchangeName: NFO, Symbol: "
        + symbol
        + ", buy_or_sell: "
        + buy_or_sell
        + ", quantity: "
        + str(quantity)
        + ", price: "
        + str(price)
        + "order_type"
        + order_type
    )

    # BUY SELL OR COMMENT FOR BOTH  BUY_SELL  BUY  SELL

    #trigger_price=trigger_price,

    discloseqty = quantity
    amo = "regular"
    symb = symbol
    paperTrading = 0
    if buy_or_sell == "BUY":
        buy_or_sell = "B"
    else:
        buy_or_sell = "S"


    if order_type == "MARKET":
        order_type = "MKT"

    elif order_type == "LIMIT":
        order_type = "LMT"
        #trigger_price=None
        discloseqty = 0

    elif order_type == "SL-LMT":
        order_type = "SL-LMT"
        discloseqty = 0

    try:
        if paperTrading == 0:
            order_id = api.place_order(
                buy_or_sell=buy_or_sell,
                product_type="M",
                exchange="NFO",
                tradingsymbol=symb,
                quantity=quantity,
                discloseqty=discloseqty,
                price_type=order_type,
                price=price,
                trigger_price=price,
                amo=amo,
                retention="DAY",
            )
            print(" => ", symb, order_id["norenordno"])
            previous_orderNo = order_id["norenordno"]
            return order_id["norenordno"]
        else:
            order_id = 0
            return order_id
    except Exception as e:
        raise Exception("NOT ABLE TO PLACE THE ORDER: ", e)


feed_opened = False
order_status_websocket = {}

def manage_add_stop_loss_limit(message):
    global sl_order_id, target_order_id, previous_quantity, previous_symbol, entry_price
    # Extract the 'norenordno' value from the JSON
    norenordno = message.get("norenordno")
    # Check if 'norenordno' matches either 'orderNo1' or 'orderNo2'
    if norenordno == str(sl_order_id):
        # if sl hit exit all quantity
        status = message.get("status")
        if status == "COMPLETE":
            reset_variables()
   


def event_handler_order_update(message):
    print(" event_handler_order_update() ")
    manage_add_stop_loss_limit(message)


def event_handler_quote_update(tick):
    global LTPDICT
    print()
    key = tick["e"] + "|" + tick["tk"]
    LTPDICT[key] = tick["lp"]
    print(LTPDICT)


def open_callback():
    global socket_opened
    socket_opened = True
    # print('app is connected')
    # api.subscribe('NSE|11630', feed_type='d')
    # api.subscribe(instrumentList)



def websocket_tick_order():
    print(" websocket_tick_order() ")
    global feed_opened
    ret = api.start_websocket(
        order_update_callback=event_handler_order_update,
        subscribe_callback=event_handler_quote_update,
        socket_open_callback=open_callback,
    )
    time.sleep(2)
    while feed_opened == False:
        pass
    return True


# Main program starts here
if __name__ == "__main__":
    # Create and start the thread
    tick_thread = threading.Thread(target=websocket_tick_order)
    tick_thread.start()
    # Start your Flask app
    app.run()
