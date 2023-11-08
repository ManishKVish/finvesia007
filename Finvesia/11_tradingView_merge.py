from NorenRestApiPy.NorenApi import NorenApi
from flask import Flask, request
import TFU_Class2c  # Same filename of your login python file
import pandas as pd
import re


api = TFU_Class2c.api
# BUY SELL OR COMMENT FOR BOTH  BUY_SELL  BUY  SELL

buy_or_sell_flag = "C P"

previous_symbol = None
previous_message = None
previous_quantity = None
previous_orderNo = None

entry_price = None
#it used to check we are placinng new trade or its old trade where we are making changes
#NEW OLD
not_freash_trade = "NEW"


# need to change everyday
default_quantiy= 50
nifty_list = ["NIFTY01JUN23C19000", "NIFTY01JUN23P18000"]
banknifty_list = ["BANKNIFTY25MAY23C44000", "BANKNIFTY25MAY23C44200"]

app = Flask(__name__)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')
        


@app.route('/1', methods=['GET'])
def health():
    return 'ok'


@app.route('/tradingview1', methods=['GET', 'POST'])
def buy_sell_qunatity():
    global previous_symbol, previous_message , previous_orderNo, previous_quantity, not_freash_trade
    not_freash_trade = "OLD"
    alert_data = request.get_json()
    symbol = alert_data.get('symbol')
    new_quantity = alert_data.get('quantity')
    message = alert_data.get('message') 
    # we are considering nifty only
    if previous_message == None and previous_orderNo == None and previous_quantity == None and previous_symbol == None:
        return Exception ("NO TRADE IS ACTIVE  NOT ABLE TO MODIFY IT")
    match = re.search(symbol, previous_symbol)
    if match:
        nifty_term = match.group()
        print(previous_symbol+" ARE GOING TO SELL QUANTITY "+new_quantity)
    else:
        return Exception(previous_symbol+"  AND  "+symbol +"  SYMBOL ARE NOT MATCHED ")
    order_id = placeOrder(symbol=previous_symbol, buy_or_sell=message, quantity=new_quantity,price=0)
    get_status_of_order(order_id)
    previous_quantity = previous_quantity- new_quantity
    previous_orderNo = order_id
    not_freash_trade = "NEW"
    return "ABLE TO " + message  +" " +symbol+ "  WITH QUANTITY "+new_quantity



@app.route('/tradingview', methods=['GET', 'POST'])
def receive_webhook():
    global previous_symbol, previous_message , previous_orderNo

    alert_data = request.get_json()

    symbol = alert_data.get('symbol')
    message = alert_data.get('message')
    interval = alert_data.get('interval')
    closePrice = alert_data.get('close')
    timenow = alert_data.get('timenow')
    print("symbol: " + symbol + ", message: " + message + ", interval: " + interval + ", closePrice: " + closePrice + ", timenow: " + timenow)

    variables = {'symbol': symbol, 'message': message, 'interval': interval, 'closePrice': closePrice, 'timenow': timenow}
    none_variables = [name for name, value in variables.items() if value is None]

    if none_variables:
        none_variable_names = ', '.join(none_variables)
        print(f"The following variable(s) have a value of None: {none_variable_names}")
        return f"The following variable(s) have a value of None: {none_variable_names}"
    
        #order is already there

    try:
        return get_exchange_Symbol_strikePrice_orderAreadyPlaced(symbol, message)
    except Exception as e:
        return "FAILED TO PLACE ORDER" + str(e)


def get_exchange_Symbol_strikePrice_orderAreadyPlaced(symbol, message):
    # jb b sell order ata h to hm use already lge huye order 
    global previous_symbol, previous_message , previous_orderNo
    tickerforSymbol = None
  
    if symbol == "NIFTY":
        if message == "BUY":

            if previous_orderNo == None:
                # its for new order 
                # CE and BUY
                tickerforSymbol = nifty_list[0]  # NiftyCE
            else:
                # OLD ORDER
                # its for exit order  exit order m hm n jo pe buy kiya tha use exit krna h
                 # kyo ki buy signal PE k liye exit ka kam krta h
                # PE AND SELL
                tickerforSymbol = nifty_list[1]
                message = "SELL"

        elif message == "SELL":
            if previous_orderNo == None:
                # its new order
                #PE AND  BUY
                tickerforSymbol = nifty_list[1]  # NiftyPE
                message = "BUY"
            else:
                # CE AND SELL  already buy order lga hua h
                #its not new order its old order jo ki buy order k time lagaya tha isko exit hona cahhiye
                tickerforSymbol = nifty_list[0]                   
    else:
        raise Exception("SYMBOL NOT MATCHED: " + symbol)
    
    # NIFTY25MAY23C18550   SELL
    #exit the order
    if previous_symbol == tickerforSymbol and message == "SELL" and previous_orderNo != None:
         exit_order_with_order_no(previous_orderNo,tickerforSymbol)


         

    #if check flag  after exiting the quantity we can take that CE OR PE which can be decide by the our buy sell flag
    if 'C' in tickerforSymbol and 'C' in buy_or_sell_flag:
        print("START PLACE CE BUY ORDER ")
    elif  'P' in tickerforSymbol and 'P' in buy_or_sell_flag:
        print("START PLACE PE BUY ORDER ")
    else:
        raise Exception( buy_or_sell_flag +"<=== FLAG IS SET ")


    ltp = getLTP(tickerforSymbol)
    if ltp is None:
        print("SYMBOL IS NOT VALID.")
        raise Exception("SYMBOL IS NOT VALID    ERROR OCCURRED WHILE FETCHING LTP")
    else:
        print("SYMBOL IS VALID")

    order_id = placeOrder(tickerforSymbol, message, default_quantiy, 0)
    return get_status_of_order(order_id)


def exit_order_with_order_no(orderno, symbol):
    print("===TRYING TO EXIT ORDER ===")
    try:
         api.exit_order(orderno)
         print(" EXIT ORDER WITH "+ orderno + " AND " +  symbol)
    except Exception as e:
         raise e("NOT ABLE TO EXIT ORDER  ")
            

def getLTP(symbol):
    try:
        print("inside getLtp")
        print("exch: NFO, token: " + symbol)
        ret = api.get_quotes(exchange="NFO", token=symbol)
        return float(ret['lp'])
    except Exception as e:
        print(symbol, "Failed: {}".format(e))

def get_status_of_order(orderNo):
    global previous_symbol, previous_message , entry_price, previous_orderNo, previous_quantity, not_freash_trade
    a = api.get_order_book()
    orderbook = pd.DataFrame(a)
    rejected_orders = orderbook.loc[orderbook["norenordno"] == str(orderNo)]
    
    for index, order in rejected_orders.iterrows():
        print("status:", order["status"])
        if order["status"] == "COMPLETE":
            print("ORDER COMPLETE " + order["status"] + " price " + order["avgprc"])
            entry_price =  order["avgprc"]
            previous_orderNo = orderNo
            return  ("ORDER COMPLETE " + order["status"] + " price " + order["avgprc"])
        if order["status"] == "REJECTED":
            print("ORDER HAS BEEN REJECTED PLEASE ADD NEW ORDER")
            #if order rejected no need to store order
            if not_freash_trade != "OLD":
                previous_symbol = None
                previous_message = None
                previous_orderNo  = None
                previous_quantity = None
            raise Exception("ORDER HAS BEEN REJECTED PLEASE ADD NEW ORDER")
    raise Exception("RETURN NO ORDER IN THE ORDER-BOOK WITH ORDER NUMBER " + orderNo)  # Return None if the order is not found in the order book



def placeOrder(symbol, buy_or_sell, quantity, price):
    global previous_symbol, previous_message, previous_quantity,previous_orderNo
    print("exchangeName: NFO, Symbol: " + symbol + ", buy_or_sell: " + buy_or_sell + ", quantity: " + str(quantity) + ", price: " + str(price))

    # BUY SELL OR COMMENT FOR BOTH  BUY_SELL  BUY  SELL
    amo = "regular"
    order_type = "MARKET"
    symb = symbol
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
                                        exchange="NFO",
                                        tradingsymbol=symb,
                                        quantity=quantity,
                                        discloseqty=quantity,
                                        price_type=order_type,
                                        price=price,
                                        trigger_price=price,
                                        amo=amo,
                                        retention="DAY")
                print(" => ", symb, order_id['norenordno'])   

                previous_symbol  = symbol
                if not_freash_trade != "OLD":
                    if buy_or_sell == 'B':
                        previous_message = 'BUY'
                    elif buy_or_sell == 'S':
                        previous_message = 'BUY'
                    previous_quantity = quantity
                    previous_orderNo  = order_id['norenordno']
                    return order_id['norenordno']
                
        else:
                order_id = 0
                return order_id
    except Exception as e:
                raise Exception("NOT ABLE TO PLACE THE ORDER: ", e)


if __name__ == '__main__':
    app.run()
