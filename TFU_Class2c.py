from NorenRestApiPy.NorenApi import NorenApi
#pip install path/whl
#pip install websocket_client
import pyotp

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
