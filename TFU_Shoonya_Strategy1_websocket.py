#DISCLAIMER:
#1) This sample code is for learning purposes only.
#2) Always be very careful when dealing with codes in which you can place orders in your account.
#3) The actual results may or may not be similar to backtested results. The historical results do not guarantee any profits or losses in the future.
#4) You are responsible for any losses/profits that occur in your account in case you plan to take trades in your account.
#5) TFU and Aseem Singhal do not take any responsibility of you running these codes on your account and the corresponding profits and losses that might occur.


import datetime
import time
import pandas as pd
from NorenRestApiPy.NorenApi import NorenApi
import logging
#import dill
import TFU_Class2c #Same filename of your login python file
import requests
#'NSE:Nifty 50'
my_information = {'NSE:SBIN-EQ': 'NSE|3045',
                  'NSE:NTPC-EQ': 'NSE|11630',
                  'NSE:Nifty 50': 'NSE|11630'}

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/',
                          eodhost='https://api.shoonya.com/chartApi/getdata/')

####################__INPUT__#####################

#TIME TO FIND THE STRIKE
entryHour   = 2
entryMinute = 49
entrySecond = 0


stock="NIFTY" # BANKNIFTY OR NIFTY
otm = 200  #If you put -100, that means its 100 points ITM.
SL_point = 0
PnL = 0
df = pd.DataFrame(columns=['Date','CE_Entry_Price','CE_Exit_Price','PE_Entry_Price','PE_Exit_Price','PnL'])
df["Date"] = [datetime.date.today()]
premium=100

#Time
#Find NSE price . If nse price < yesterday closing (ATM)
#ENtry Price BUY
#Exit SL == target


expiry = {
    "year": "23",
    "month": "MAR",
    "day": "02",
    #YYMDD  22O06  22OCT  22OCT YYMMM
    #YYMMM  22, N, OV
    #YYMDD   22 o/n/d   03
    #YYMDD  22  6  10   22JUN
    #Shoonya : DDMMMYY
}

clients = [
    {
        "broker": "shoonya",
        "userID": "",
        "apiKey": "",
        "accessToken": "",
        "qty" : 50
    }
]


##################################################


def findStrikePriceATM():
    print(" Placing Orders ")
    global clients
    global SL_percentage

    if stock == "BANKNIFTY":
        name = "Nifty Bank"   #"NSE:NIFTY BANK"
    elif stock == "NIFTY":
        name = "Nifty 50"       #"NSE:NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["day"]+expiry["month"]+expiry["year"]   #22OCT

    ######################################################
    #FINDING ATM
    ltp = float(getLTP("NSE",name))
    print(ltp)

    if stock == "BANKNIFTY":
        closest_Strike = int(round((ltp / 100),0) * 100)
        print(closest_Strike)

    elif stock == "NIFTY":
        closest_Strike = int(round((ltp / 50),0) * 50)
        print(closest_Strike)

    print("closest",closest_Strike)
    closest_Strike_CE = closest_Strike+otm
    closest_Strike_PE = closest_Strike-otm

    if stock == "BANKNIFTY":
        atmCE = "BANKNIFTY" + str(intExpiry)+"C"+str(closest_Strike_CE)
        atmPE = "BANKNIFTY" + str(intExpiry)+"P"+str(closest_Strike_PE)
    elif stock == "NIFTY":
        atmCE = "NIFTY" + str(intExpiry)+"C"+str(closest_Strike_CE)
        atmPE = "NIFTY" + str(intExpiry)+"P"+str(closest_Strike_PE)

    print(atmCE)
    print(atmPE)

    takeEntry(closest_Strike_CE, closest_Strike_PE, atmCE, atmPE)


def findStrikePricePremium():
    print(" Placing Orders ")
    global clients
    global SL_percentage
    global premium

    if stock == "BANKNIFTY":
        name = "Nifty Bank"
    elif stock == "NIFTY":
        name = "Nifty 50"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["day"]+expiry["month"]+expiry["year"]

    ######################################################
    #FINDING ATM
    ltp = float(getLTP("NSE",name))
    if stock == "BANKNIFTY":
        for i in range(-8, 8):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
        print(strikeList)

        #FOR CE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = float(getLTP("NFO","BANKNIFTY" + str(intExpiry)+"C"+str(strike)))
            diff = abs(ltp_option - premium)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike_CE = strike
                prev_diff = diff
            time.sleep(.5)

        #FOR PE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = float(getLTP("NFO","BANKNIFTY" + str(intExpiry)+"P"+str(strike)))
            diff = abs(ltp_option - premium)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike_PE = strike
                prev_diff = diff
            time.sleep(.5)


    elif stock == "NIFTY":
        for i in range(-5, 5):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
            strikeList.append(strike+50)
        print(strikeList)

        #For CE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = float(getLTP("NFO","NIFTY" + str(intExpiry)+"C"+str(strike)))
            diff = abs(ltp_option - premium)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike_CE=strike
                prev_diff=diff
            time.sleep(.5)

        #For PE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = float(getLTP("NFO","NIFTY" + str(intExpiry)+"P"+str(strike)))
            diff = abs(ltp_option - premium)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike_PE=strike
                prev_diff=diff
            time.sleep(.5)

    print("closest CE",closest_Strike_CE)
    print("closest PE",closest_Strike_PE)

    if stock == "BANKNIFTY":
        atmCE = "BANKNIFTY" + str(intExpiry)+"C"+str(closest_Strike_CE)
        atmPE = "BANKNIFTY" + str(intExpiry)+"P"+str(closest_Strike_PE)
    elif stock == "NIFTY":
        atmCE = "NIFTY" + str(intExpiry)+"C"+str(closest_Strike_CE)
        atmPE = "NIFTY" + str(intExpiry)+"P"+str(closest_Strike_PE)

    print(atmCE)
    print(atmPE)

    takeEntry(closest_Strike_CE, closest_Strike_PE, atmCE, atmPE)



def takeEntry(closest_Strike_CE, closest_Strike_PE, atmCE, atmPE):
    global SL_point
    global PnL
    ce_entry_price = float(getLTP("NFO",atmCE))
    pe_entry_price = float(getLTP("NFO",atmPE))
    PnL = ce_entry_price + pe_entry_price
    print("Current PnL is: ", PnL)
    df['CE_Entry_Price'] = [ce_entry_price]
    df['PE_Entry_Price'] = [pe_entry_price]

    print(" closest_CE ATM ", closest_Strike_CE, " CE Entry Price = ", ce_entry_price)
    print(" closest_PE ATM", closest_Strike_PE, " PE Entry Price = ", pe_entry_price)

    ceSL = round(ce_entry_price + SL_point, 1)
    peSL = round(pe_entry_price + SL_point, 1)
    print("Placing Order CE Entry Price = ", ce_entry_price, "|  CE SL => ", ceSL)
    print("Placing Order PE Entry Price = ", pe_entry_price, "|  PE SL => ", peSL)

    #SELL AT MARKET PRICE
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        print("userID = ", client['userID'])
        broker = client['broker']
        uid = client['userID']
        key = client['apiKey']
        token = client['accessToken']
        qty = client['qty']

        oidentryCE = 0
        oidentryPE = 0

        oidentryCE = placeOrderShoonya( atmCE, "SELL", qty, "MARKET", 0, "regular")
        oidentryPE = placeOrderShoonya( atmPE, "SELL", qty, "MARKET", 0, "regular")

        print("The OID of Entry CE is: ", oidentryCE)
        print("The OID of Entry PE is: ", oidentryPE)

        exitPosition(atmCE, ceSL, ce_entry_price, atmPE, peSL, pe_entry_price, qty)


def exitPosition(atmCE, ceSL, ce_entry_price, atmPE, peSL, pe_entry_price, qty):
    global PnL
    traded = "No"

    while traded == "No":
        dt = datetime.datetime.now()
        try:
            ltp = float(getLTP("NFO",atmCE))
            ltp1 = float(getLTP("NFO",atmPE))
            if ((ltp > ceSL) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                oidexitCE = placeOrderShoonya( atmCE, "BUY", qty, "MARKET", 0, "regular")
                PnL = PnL - ltp
                print("Current PnL is: ", PnL)
                df["CE_Exit_Price"] = [ltp]
                print("The OID of Exit CE is: ", oidexitCE)
                traded = "CE"
            elif ((ltp1 > peSL) or (dt.hour >= 15 and dt.minute >= 15)) and ltp1 != -1:
                oidexitPE = placeOrderShoonya( atmPE, "BUY", qty, "MARKET", 0, "regular")
                PnL = PnL - ltp1
                print("Current PnL is: ", PnL)
                df["PE_Exit_Price"] = [ltp1]
                print("The OID of Exit PE is: ", oidexitPE)
                traded = "PE"
            else:
                print("NO SL is hit: "+"LTP CE: ",ltp," LTP PE: ",ltp1)
                time.sleep(1)

        except:
            print("Couldn't find LTP , RETRYING !!")
            time.sleep(1)

    if (traded == "CE"):
        peSL = pe_entry_price
        while traded == "CE":
            dt = datetime.datetime.now()
            try:
                ltp = float(getLTP("NFO",atmPE))
                if ((ltp > peSL) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitPE = placeOrderShoonya( atmPE, "BUY", qty, "MARKET", 0, "regular")
                    PnL = PnL - ltp
                    print("Current PnL is: ", PnL)
                    df["PE_Exit_Price"] = [ltp]
                    print("The OID of Exit PE is: ", oidexitPE)
                    traded = "Close"
                else:
                    print("PE SL not hit")
                    time.sleep(1)

            except:
                print("Couldn't find LTP , RETRYING !!")
                time.sleep(1)

    elif (traded == "PE"):
        ceSL = ce_entry_price
        while traded == "PE":
            dt = datetime.datetime.now()
            try:
                ltp = float(getLTP("NFO",atmCE))
                if ((ltp > ceSL) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitCE = placeOrderShoonya( atmCE, "BUY", qty, "MARKET", 0, "regular")
                    PnL = PnL - ltp
                    df["CE_Exit_Price"] = [ltp]
                    print("Current PnL is: ", PnL)
                    print("The OID of Exit CE is: ", oidexitCE)
                    traded = "Close"
                else:
                    print("CE SL not hit")
                    time.sleep(1)
            except:
                print("Couldn't find LTP , RETRYING !!")
                time.sleep(1)

    elif (traded == "Close"):
        print("All trades done. Exiting Code")


def getLTP(exch,token):
    instrument = exch+":"+token
    instrument = my_information[instrument]
    url = "http://localhost:4002/ltp?instrument=" + instrument
    try:
        resp = requests.get(url)
    except Exception as e:
        print(e)
    data = resp.json()
    return data



def checkTime_tofindStrike():
    x = 1
    while x == 1:
        dt = datetime.datetime.now()
        if( dt.hour >= entryHour and dt.minute >= entryMinute and dt.second >= entrySecond ):
            print("time reached")
            x = 2
            findStrikePriceATM()
            #findStrikePricePremium()
        else:
            time.sleep(.1)
            print(dt , " Waiting for Time to check new ATM ")




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



#EITHER THIS
#api = ShoonyaApiPy()
#with open ('api.dill', 'rb') as fp:
#    api = dill.load(fp)
#    print(api)

#OR THIS
api =TFU_Class2c.api

checkTime_tofindStrike()
df["PnL"] = [PnL]
df.to_csv('Str1_Shoonya_websocket.csv',mode='a',index=True,header=True)
