from NorenRestApiPy.NorenApi import NorenApi
from flask import Flask, request
import TFU_Class2c  # Same filename of your login python file
import pandas as pd
import re
import threading
from queue import Queue
import requests
import threading
from queue import Queue
import time
import datetime


app = Flask(__name__)


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(
            self,
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
            eodhost="https://api.shoonya.com/chartApi/getdata/",
        )


api = TFU_Class2c.api
# -VE      IN THE MONEY
# 0  ATM
# +VE     OUT THE MONEY

# no trade time zone
no_trade_time_start_hour= 10
no_trade_time_start_min= 45

no_trade_time_end_hour= 1
no_trade_time_end_min= 0

target_percent = 1.10
sl_percent = 0.90
otm = -100
default_quantiy = 100

expiry = {
    "year": "23",
    "month": "SEP",
    "day": "14"
}


# BUY SELL OR COMMENT FOR BOTH  BUY_SELL  BUY  SELL

buy_or_sell_flag = "C_BUY P_BUY"
previous_symbol = None
entry_price = None
previous_quantity = None
fst_target = None
fst_target_order_no = None
trade = None
closePrice = None



target_order_id = None
sl_order_id = None


stop_event = threading.Event()
loop = False
# quantity should be multiple of 100

last_postion = "HALF"
stock = "NIFTY"

my_information = {
    "NSE:NIFTY": "NSE|26000",
    "NSE:BANKNIFTY": "NSE|26009",
}


##################################################


def getLTP_websocket(exch, token):
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
    if closePrice != None:
        ltp = closePrice
    else:
        ltp = float(getLTP("NSE", stock))
    print(f" {stock} ==> {ltp}")

    ltp = float(ltp)

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


@app.route("/1m", methods=["GET"])
def health():
    return "API is up"

@app.route("/obp", methods=["GET"])
def get_last_position():
    global previous_symbol, entry_price ,previous_quantity, target_percent, sl_percent , default_quantiy, sl_exit , fst_target
    print(" inside get_last_position() ")
    lprice = None
    quantity = None

    try:
        json = api.get_positions()
        if json != None:
            if json[0]['stat'] == 'Ok':     
                    quantity = int(json[0]['netqty'])
                    if quantity != None and quantity != 0:
                        previous_quantity = quantity
                        previous_symbol = json[0]['tsym']
                        entry_price = float(json[0]['dayavgprc'])
                        lprice = float(json[0]['lp'])
                    else:
                        print("No Active Position")
                        return "No Active Position"
        else:
            print("No Active Position")
            return "No Active Position"
    except Exception as e:
        print(" NOT ABLE TO FEATCH POSITION "+ e)
   
    if previous_symbol != None and previous_quantity != 0:
        if previous_quantity < default_quantiy and previous_quantity != 0:
            sl_exit =format(entry_price, ".1f")
        
        if previous_quantity == default_quantiy:

            fst_target = float(target_percent) * float(entry_price)
            fst_target = format(fst_target, ".1f")

            sl_exit = float(sl_percent) * float(entry_price)
            sl_exit = format(sl_exit, ".1f")  


        if previous_quantity > default_quantiy:
            return " previous quantity is grater than default quantity "

        target_sl()

    return f"SYMBOL  =>{previous_symbol} QUANTITY => {previous_quantity}  EP => {entry_price}  LTP => {lprice} EP =>  {fst_target}  EP => {sl_exit} "


@app.route("/1m/ob_set", methods=["GET", "POST"])
def set_value():

    global previous_symbol, previous_orderNo, previous_quantity, not_freash_trade, default_quantiy, fst_target, fst_target_order_no, sl_exit, loop, last_postion, entry_price
    alert_data = request.get_json()
    quantity = alert_data.get("quantity")
    if previous_quantity != None:
        previous_quantity = quantity
    if previous_quantity != None:
        print("NEW PREVIOUS QUANTITY : " + previous_quantity)



@app.route("/1m/ob_add", methods=["GET", "POST"])
def buy_sell_qunatity():
    global previous_symbol, previous_message, previous_orderNo, previous_quantity, not_freash_trade
    not_freash_trade = "OLD"
    alert_data = request.get_json()
    symbol = alert_data.get("symbol")
    new_quantity = alert_data.get("quantity")
    message = alert_data.get("message")
    # we are considering nifty only
    if (
        previous_message == None
        and previous_orderNo == None
        and previous_quantity == None
        and previous_symbol == None
    ):
        return Exception("NO TRADE IS ACTIVE  NOT ABLE TO MODIFY IT")
    match = re.search(symbol, previous_symbol)
    if match:
        nifty_term = match.group()
        print(previous_symbol + " ARE GOING TO SELL QUANTITY " + new_quantity)
    else:
        return Exception(
            previous_symbol + "  AND  " + symbol + "  SYMBOL ARE NOT MATCHED "
        )
    order_id = placeOrder(
        symbol=previous_symbol,
        buy_or_sell=message,
        quantity=new_quantity,
        price=0,
        order_type="MARKET",
    )
    get_status_of_order(order_id)
    previous_quantity = previous_quantity - new_quantity
    previous_orderNo = order_id
    not_freash_trade = "NEW"
    return "ABLE TO " + message + " " + symbol + "  WITH QUANTITY " + new_quantity

@app.route("/1m/sell", methods=["GET", "POST"])
def receive_webhook():

    global previous_symbol, previous_message, previous_orderNo, closePrice,trade, previous_quantity, trade,sl_order_id
    alert_data = request.get_json()
    message = alert_data.get("message")
    closePrice1 = alert_data.get("close")
    if previous_symbol != None:
        if (float(float(closePrice1)+20)) >= float(closePrice):
    # if we  message == "SELL" send half from there it will sell half quantity 
            try:
                if message == "SELL":
                    order_id = placeOrder(symbol=previous_symbol,
                    buy_or_sell="SELL",
                    quantity=previous_quantity,
                    price=0,
                    order_type="MARKET",
                )  
                api.cancel_order(sl_order_id)
                reset_variables()


        # if we  message == "HALF" send half from there it will sell half quantity 

                if message == "HALF":
                    order_id = placeOrder(
                    symbol=previous_symbol,
                    buy_or_sell="SELL",
                    quantity= (float(previous_quantity) / 2),
                    price=0,
                    order_type="MARKET",
                ) 
                    previous_quantity =(float(previous_quantity) / 2)

                # placing the sl - limit order at entry
                
                api.cancel_order(sl_order_id)
                sl_order_id = placeOrder(previous_symbol, "SELL", previous_quantity, entry_price, "SL-LMT")
                
                print(" ABLE TO EXIT QUANTITY" +previous_quantity +"  AND SYMBOL "+previous_symbol)
                return (" ABLE TO EXIT QUANTITY" +previous_quantity +"  AND SYMBOL "+previous_symbol)
            
            except Exception as e:
                print(" NOT ABLE TO EXIT QUANTITY")
                return " NOT ABLE TO EXIT QUANTITY"
        print(" SELLING PRICE IS NEAR TO THE ENTRY PRICE CAN NOT EXIT")
        return "SELLING PRICE IS NEAR TO THE ENTRY PRICE CAN NOT EXIT"
    print(" NO ACTIVE TRADE")
    return "NO ACTICE TRADE"







@app.route("/1m/ob", methods=["GET", "POST"])
def receive_webhook2():

    global previous_symbol, previous_message, previous_orderNo, closePrice,trade
    alert_data = request.get_json()
    symbol = alert_data.get("symbol")
    message = alert_data.get("message")
    quantity = alert_data.get("quantity")
    interval = alert_data.get("interval")
    closePrice = alert_data.get("close")
    timenow = alert_data.get("timenow")
    trade = alert_data.get("trade")

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


# calling this method to setting variable
@app.route("/1m/None", methods=["GET"])
def reset_variables():
    global previous_symbol
    global entry_price
    global previous_quantity
    global fst_target
    global fst_target_order_no
    global trade
    global closePrice
    global target_order_id
    global sl_order_id
    
    previous_symbol = None
    entry_price = None
    previous_quantity = None
    fst_target = None
    fst_target_order_no = None
    trade = None
    closePrice = None
    target_order_id = None
    sl_order_id = None
    print("ALL VARIABLE IS NONE")
    return "ALL VARIABLE IS NONE"



def getToken(exch, symbol):
    try:
        output = api.searchscrip(exchange=exch, searchtext=symbol)
        return output["values"][0]["token"]
    except Exception as e:
        print(" NOT ABLE TO FIND TOKEN FOR SYMBOL" + str(e))


def get_exchange_Symbol_strikePrice_orderAreadyPlaced(symbol, message):
    print(" Create two threads for method1 and method2 ")
    global previous_message, previous_symbol, loop, previous_quantity, trade
    loop = False

    if sl_order_id != None:
            api.cancel_order(sl_order_id)
    if target_order_id != None:
            api.cancel_order(target_order_id)

# if last trade active than we just exit the trade we will not take any new trade
    if previous_symbol != None and previous_quantity != None:
        if "C" in previous_symbol and "C" in message:
        # if last trade is ce exit only ce exit
            string1 = exit_order(symbol, message)
        if "P" in previous_symbol and "P" in message:
        # if last trade is ce exit only ce exit
            string1 = exit_order(symbol, message)

    

    elif previous_symbol is None and previous_quantity is None and trade == "ME":
        # Create two threads for method1 and method2
        string1 = None
        string2 = None
        try:
            # Create a result queue
            result_queue = Queue()

            def exit_order__thread():
                print("inside exit_order__thread")
                nonlocal string1
                try:
                    string1 = exit_order(symbol, message)
                    result_queue.put(string1)  # Put the result in the queue
                except Exception as e:
                    print(f"Exception occurred in thread1_fun  SELL ORDERc: {e}")
                    return f"Exception occurred in exit_order__thread SELL ORDER: {e}"
                    # raise Exception(f" SELL ORDER : {e}")

            def entry_order_thread():
                print("inside entry_order_thread")
                nonlocal string2
                try:
                    string2 = entry_order(symbol, message)
                    result_queue.put(string2)  # Put the result in the queue
                except Exception as e:
                    print(f"Exception occurred in entry_order_thread BUY ORDER: {e}")
                    return f"Exception occurred in entry_order_thread BUY ORDER: {e}"
                # Create thread objects

            thread1 = threading.Thread(target=exit_order__thread)
            thread2 = threading.Thread(target=entry_order_thread)

            # Start both threads

            thread1.start()
            time.sleep(0.01)
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
# SYMBOL NIFTY
# SELL P_BUY AND C_SELL
# NIFTY01JUN23C19000
def exit_order(symbol, message):


    print(" exit_order () ")
    global previous_symbol, previous_quantity, sl_order_id, target_order_id, trade, closePrice, entry_price

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
        
        order_id = placeOrder(
                previous_symbol, "SELL", previous_quantity, 0, "MARKET"
            )
        
       # previous_quantity = None
       # previous_symbol = None
       # trade = None
        reset_variables()
        return get_status_of_order(order_id)
    
    else:
        print("PREVIOUS TRADE != ACTIVE : NO SELL ORDER")
        return "PREVIOUS TRADE != ACTIVE : NO SELL ORDER"
    print("NOT ABLE TO EXIT QUANTITY")


# OPtions BUY order
def entry_order(symbol, message):
    print(" entry_order() ")
    global previous_symbol, previous_quantity, last_postion, fst_target, fst_target_order_no, loop, no_trade_time_start_hour, no_trade_time_start_min, no_trade_time_end_hour,no_trade_time_end_min

    current_time = datetime.datetime.now().time()

    start_time = datetime.time(no_trade_time_start_hour, no_trade_time_start_min)
    end_time = datetime.time(no_trade_time_end_hour, no_trade_time_end_min)

    if start_time <= current_time <= end_time:
        print("NO TRADE :: TIME IS BETWEEN 10:45 == 11:00")
        return "NO TRADE :: TIME IS BETWEEN 10:45 == 11:00"
    else:
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
                    last_postion = "FULL"
                    target_sl()
                    # 1st target
                    print(
                        " TRYING TO PLACE 1ST TARGET ORDER FOR SYMBOL "
                        + previous_symbol
                        + " AT "
                        + str(fst_target)
                    )
                    print(
                        " ORDER COMPLETE WITH "
                        + previous_symbol
                        + " AND QUANTITY "
                        + str(previous_quantity)
                        + " LAST POSTION FLAG "
                        + last_postion
                    )
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
                    target_sl()
                    print(
                        " ORDER COMPLETE WITH "
                        + previous_symbol
                        + " AND QUANTITY "
                        + str(previous_quantity)
                        + " LAST POSTION FLAG "
                        + last_postion
                    )
                    # 1st target
                    print(
                        " TRYING TO PLACE 1ST TARGET ORDER FOR SYMBOL "
                        + previous_symbol
                        + " AT "
                        + str(fst_target)
                    )
                # i want to call a method which run in background check ltp is reaches to 1.1*entry_price it shold print exit half quantity
                return string1
            raise Exception("PE :: BUYING != THERE IN THE FLAG")
        else:
            print("OPTION SYMBOL NOT FOUND FOR THE GIVEN SYMBOL AND MESSAGE.")
    


def target_sl():
    global target_order_id, sl_order_id
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


def get_status_of_order_for_exit_quantity(orderNo):
    print(" get_status_of_order_for_exit_quantity() ")
    global previous_quantity, last_postion
    a = api.get_order_book()
    orderbook = pd.DataFrame(a)
    rejected_orders = orderbook.loc[orderbook["norenordno"] == str(orderNo)]
    for index, order in rejected_orders.iterrows():
        print("status:", order["status"])
        if order["status"] == "COMPLETE":
            print("ORDER COMPLETE " + order["status"] + " price " + order["avgprc"])
            previous_quantity = previous_quantity / 2
            last_postion = "HALF"
            return order["status"]
        if order["status"] == "REJECTED":
            print("ORDER HAS BEEN REJECTED PLEASE ADD NEW ORDER")
            return order["status"]
        if order["status"] == "PENDING":
            print("ORDER HAS BEEN ADDED")
            return order["status"]
        if order["status"] == "OPEN":
            print("ORDER HAS BEEN OPEN  ")
            return order["status"]
    raise Exception("RETURN NO ORDER IN THE ORDER-BOOK WITH ORDER NUMBER " + orderNo)


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


def manage_target_sl(message):
    global sl_order_id, target_order_id, previous_quantity, previous_symbol, entry_price, trade
    # Extract the 'norenordno' value from the JSON
    norenordno = message.get("norenordno")
    # Check if 'norenordno' matches either 'orderNo1' or 'orderNo2'
    if norenordno == str(sl_order_id):
        # if sl hit exit all quantity
        status = message.get("status")
        if status == "COMPLETE":
            if target_order_id != None:
                api.cancel_order(target_order_id)
            reset_variables()



def event_handler_order_update(message):
    print(" event_handler_order_update() ")
    manage_target_sl(message)


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


# end of callbacks


def get_time(time_string):
    data = time.strptime(time_string, "%d-%m-%Y %H:%M:%S")
    return time.mktime(data)


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
