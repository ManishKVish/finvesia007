#DISCLAIMER:
#1) This sample code is for learning purposes only.
#2) Always be very careful when dealing with codes in which you can place orders in your account.
#3) The actual results may or may not be similar to backtested results. The historical results do not guarantee any profits or losses in the future.
#4) You are responsible for any losses/profits that occur in your account in case you plan to take trades in your account.
#5) TFU and Aseem Singhal do not take any responsibility of you running these codes on your account and the corresponding profits and losses that might occur.


import threading
import time

from datetime import datetime,timedelta
from pytz import timezone
import ta    #Python TA Lib
import pandas as pd
import pandas_ta as pta    #Pandas TA Libv
from NorenRestApiPy.NorenApi import NorenApi
import os
#import dill
import TFU_Class2c #Same filename of your login python file


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')


#This function helps to create OHLC candles. You have to pass the stock name + timeframe
def ohlc(checkInstrument,timeframe):
    date=pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
    while(str(date)[-2::]!='00'):
        date=pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
    date=date+timedelta(minutes=timeframe)
    current=date
    date=date-timedelta(seconds=2)
    l=[]
    while(pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))<=date):
        x=getLTP("NFO",checkInstrument)
        time.sleep(1)
        if x!=-1:
            l.append(x)
    if l!=[]:
        opens=l[0]
        high=max(l)
        low=min(l)
        close=l[-1]
        return [current,opens,high,low,close]
    else:
        return [-1]

def getLTP(exch,token):
    try:
        ret = api.get_quotes(exchange=exch, token=token)
        return float(ret['lp'])

    except Exception as e:
        print(token , "Failed : {} ".format(e))



def findStrikePriceATM(stock, cepe):
    global tradeCEoption
    global tradePEoption
    print(" Finding ATM ")
    global kc
    global clients
    global SL_percentage

    if (stock == "BANKNIFTY"):
        name = "Nifty Bank"   #"NSE:NIFTY BANK"
    elif (stock == "NIFTY"):
        name = "Nifty 50"       #"NSE:NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["day"]+expiry["month"]+expiry["year"]   #22OCT

    ######################################################
    #FINDING ATM
    ltp = getLTP("NSE",name)

    if stock == "BANKNIFTY":
        closest_Strike = int(round((ltp / 100),0) * 100)
        print(closest_Strike)

    elif stock == "NIFTY":
        closest_Strike = int(round((ltp / 50),0) * 50)
        print(closest_Strike)

    print("closest",closest_Strike)
    closest_Strike_CE = closest_Strike+otm
    closest_Strike_PE = closest_Strike-otm

    if (stock == "BANKNIFTY"):
        atmCE = "BANKNIFTY" + str(intExpiry)+"C"+str(closest_Strike_CE)
        atmPE = "BANKNIFTY" + str(intExpiry)+"P"+str(closest_Strike_PE)
    elif (stock == "NIFTY"):
        atmCE = "NIFTY" + str(intExpiry)+"C"+str(closest_Strike_CE)
        atmPE = "NIFTY" + str(intExpiry)+"P"+str(closest_Strike_PE)

    print(atmCE)
    print(atmPE)

    if (cepe == "CE"):
        #BUY AT MARKET PRICE
        print("In CE placeorder")
        for client in clients:
            print("\n============_Placing_Trades_=====================")
            print("userID = ", client['userID'])
            broker = client['broker']
            uid = client['userID']
            key = client['apiKey']
            token = client['accessToken']
            qty = client['qty']
            oidentry = placeOrderShoonya( atmCE, "BUY", qty, "MARKET", 0, "regular")
            tradeCEoption = atmCE
    else:
        #BUY AT MARKET PRICE
        print("In PE placeorder")
        for client in clients:
            print("\n============_Placing_Trades_=====================")
            print("userID = ", client['userID'])
            broker = client['broker']
            uid = client['userID']
            key = client['apiKey']
            token = client['accessToken']
            qty = client['qty']
            oidentry = placeOrderShoonya( atmPE, "BUY", qty, "MARKET", 0, "regular")
            tradePEoption = atmPE

    return oidentry



def exitPosition(tradeOption):
    #Sell existing option
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        print("userID = ", client['userID'])
        broker = client['broker']
        uid = client['userID']
        key = client['apiKey']
        token = client['accessToken']
        qty = client['qty']
        oidentry = placeOrderShoonya( tradeOption, "SELL", qty, "MARKET", 0, "regular")
        return oidentry

def placeOrderShoonya(inst, buy_or_sell, qty, order_type, price, amo):
    global api
    exch = "NFO"
    symb = inst
    paperTrading = 1 #if this is 0, then real trades will be placed
    if( buy_or_sell=="BUY"):
        buy_or_sell="B"
    else:
        buy_or_sell="S"

    if(order_type=="MARKET"):
        order_type="MKT"
    elif(order_type=="LIMIT"):
        order_type="LMT"

    try:
        if(paperTrading == 0):
            order_id = api.place_order(buy_or_sell=buy_or_sell,  #B, S
                                       product_type="I", #C CNC, M NRML, I MIS
                                       exchange=exch,
                                       tradingsymbol=symb,
                                       quantity = qty,
                                       discloseqty=qty,
                                       price_type= order_type, #LMT, MKT, SL-LMT, SL-MKT
                                       price = price,
                                       trigger_price=price,
                                       amo=amo,#YES, NO
                                       retention="DAY"
                                       )
            print(" => ", symb , order_id['norenordno'] )
            return order_id['norenordno']

        else:
            order_id=0
            return order_id

    except Exception as e:
        print(" => ", symb , "Failed : {} ".format(e))

####################__INPUT__#####################

#EITHER THIS
#api = ShoonyaApiPy()
#with open ('api.dill', 'rb') as fp:
#    api = dill.load(fp)
#    print(api)

#OR THIS
api =TFU_Class2c.api


checkInstrument = "NIFTY24NOV22F";
tradeCEoption = ""
tradePEoption = ""

clients = [
    {
        "broker": "zerodha",
        "userID": "",
        "apiKey": "",
        "accessToken": "",
        "qty" : 50
    }
]

expiry = {
    "year": "23",
    "month": "MAR",
    "day": "02",
}
otm = 0

x = 1
close=[]   #close[17873, 17777, 17772]
opens=[]
high=[]
low=[]


#-----------If there is any previous data, we will copy it------------
p = os.path.join(os.getcwd(), 'lists.csv')
if os.path.isfile(p):
    df_read = pd.read_csv('lists.csv')
    for i in range(0,len(df_read)):
        close.insert(len(close),df_read['close'][i])
        opens.insert(len(opens),df_read['opens'][i])
        high.insert(len(high),df_read['high'][i])
        low.insert(len(low),df_read['low'][i])


op=['supertrend',2,1]
print(['datetime','open','high','low','close'])
gt=1
lt=1
xx = 2
firsttrade = 0
while x == 1:
    data=ohlc(checkInstrument,1)  #[9:20, 17000, 17870, 16780, 17220, 17556] timeframe
    dt1 = datetime.now()
    if data[0]!=-1:
        opens.append(data[1])
        high.append(data[2])
        low.append(data[3])
        close.append(data[-1])
        st=''
        if op!=[]:
            if op[0]=='sma':
                value=ta.trend.SMAIndicator(pd.Series(close),op[1]).sma_indicator().iloc[-1]
            elif op[0]=='supertrend':
                value=pd.DataFrame(pta.supertrend(pd.Series(high),pd.Series(low),pd.Series(close),op[1],op[2]))
                if value.empty==False :
                    value=value.iloc[-1][0]
                    st=value
                    print("st: ",st)
                else:
                    value='nan'
        data.append(value)
        print("here")
        print("st: ",st)
        print("close: ",close[-1])

        if st!='' and close[-1]>st and gt==1 and st!='nan':
            if firsttrade == 0:
                print("This is the first trade. Supertrend green")
                firsttrade = 1;
                #BUYING CE
                oidentry = findStrikePriceATM("NIFTY", "CE")

            else:
                print('Close Greater then Supertrend. So supertrend is green. Buy CE/Sell PE and exit last position')
                #BUYING CE
                oidentry = findStrikePriceATM("NIFTY", "CE")
                time.sleep(1)
                #Exit PE
                oidexit = exitPosition(tradePEoption)

            gt=0
            lt=1
        elif st!='' and close[-1]<st and lt==1 and st!='nan':
            if firsttrade == 0:
                print("This is the first trade. Supertrend Red")
                firsttrade = 1;
                #BUYING PE
                oidentry = findStrikePriceATM("NIFTY", "PE")

            else:
                print('Close Less then Supertrend. So supertrend is red. Buy PE/Sell CE and exit last position')
                #BUYING PE
                oidentry = findStrikePriceATM("NIFTY", "PE")
                time.sleep(1)
                #Exit CE
                oidexit = exitPosition(tradeCEoption)
            lt=0
            gt=1
        #elif pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')) > pd.to_datetime(str(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'))+'03:15:00'):
        elif (dt1.hour >= 15 and dt1.minute >= 15):
            if lt == 0:
                print("EOD. Current open trade is based on Supertrend Red")
                #Exit Position
                oidexit = exitPosition(tradePEoption)
            elif gt == 0:
                print("EOD. Current open trade is based on Supertrend Green")
                #Exit position
                oidexit = exitPosition(tradeCEoption)
            print('End Of the Day')
            break
        print(data)


#------------Saving the final lists in csv file------------------
df_write = pd.DataFrame(columns=['opens','close','high','low'])

for i in range(0,len(opens)):
    df1 = {'opens':opens[i], 'close':close[i], 'high':high[i], 'low':low[i]}
    df_write = df_write.append(df1, ignore_index = True)

df_write.to_csv('lists.csv', index = False)
