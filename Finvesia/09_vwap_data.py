from api_helper import ShoonyaApiPy

import yaml

import datetime



with open('cred.yml') as f:

    cred = yaml.load(f, Loader=yaml.FullLoader)

    # print(cred)



api = ShoonyaApiPy()

ret = api.login(userid = cred['user'], password = cred['pwd'], twoFA=cred['factor2'], vendor_code=cred['vc'], api_secret=cred['apikey'], imei=cred['imei'])



lastBusDay = datetime.datetime.today()

lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0, day=8, month=4)



sStrike = 'BANKNIFTY21APR22P37500'



OptToken = api.searchscrip(exchange="NFO", searchtext=sStrike)

sToken = str(OptToken['values'][0]['token'])



ret = api.get_time_price_series(exchange='NFO', token=sToken, starttime=lastBusDay.timestamp(), interval=1)



print('Strike: ' + sStrike)

print('LTP: ' + ret[0]['intc'])

print('VWAP: ' + ret[0]['intvwap'])



ret1 = api.get_quotes('NFO', sToken)

print('VWAP: ' + ret1['ap'])