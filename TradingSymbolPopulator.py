import datetime
import time
import pandas as pd
import csv
import os

def instrumentListForSubscribeFile(symbol,expiryDate,tradingIndexValue):
    if(symbol=='BANKNIFTY'):
          indexRange=1000
    else:
        indexRange=500
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'NIFTY_BANKNIFTY_Symbols.csv'),'r') as read_obj:
            csv_reader = csv.reader(read_obj)
            list_of_symbols = list(csv_reader)
            instrumentListForSubscribe = ['NSE|26009', 'NSE|26000']
            for csvSymbol in list_of_symbols:
                    if csvSymbol[3]==symbol and csvSymbol[5]==expiryDate:
                        tradingSymbol = csvSymbol[4]
                        tempIndex=len(tradingSymbol)-5
                        tradingIndexCsvValue=int(tradingSymbol[tempIndex:])
                        if(abs(tradingIndexValue-tradingIndexCsvValue)<=indexRange):
                            token = csvSymbol[1]
                            tradingSymbol = csvSymbol[4]
                            instrumentListForSubscribe.append('NFO|'+token)
    return instrumentListForSubscribe

def instrumentListForStrategyFile(symbol,expiryDate, tradingIndexValue):
    if(symbol=='BANKNIFTY'):
          indexRange=1000
    else:
        indexRange=500

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'NIFTY_BANKNIFTY_Symbols.csv'),'r') as read_obj:
            csv_reader = csv.reader(read_obj)
            list_of_symbols = list(csv_reader)
            instrumentListForStrategy = {'NSE|Nifty Bank': 'NSE|26009', 'NSE|Nifty 50' : 'NSE|26000'}
            for csvSymbol in list_of_symbols:
                    if csvSymbol[3]==symbol and csvSymbol[5]==expiryDate:
                        tradingSymbol = csvSymbol[4]
                        tempIndex=len(tradingSymbol)-5
                        tradingIndexCsvValue=int(tradingSymbol[tempIndex:])
                        if(abs(tradingIndexValue-tradingIndexCsvValue)<=indexRange):
                            token = csvSymbol[1]
                            tradingSymbol = csvSymbol[4]
                            instrumentListForStrategy['NFO|'+tradingSymbol]='NFO|'+token+''
            
    return instrumentListForStrategy
            
# subscribeSymbolList = instrumentListForSubscribeFile('BANKNIFTY', '09-Mar-23',41000)
# print(subscribeSymbolList)
# print("******************************************************************************")
strategySymbolList = instrumentListForStrategyFile('BANKNIFTY', '09-Mar-23', 41000)
print(strategySymbolList)