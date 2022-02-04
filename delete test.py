import pyupbit
import datetime
import time
import requests

#Alarm 과 Autotrade 되도록

access = "access"
secret = "secret"
myToken = "myToken"


def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

def get_ma30(ticker):
    ma30 = pyupbit.get_ohlcv(ticker, "minute30")['close'].rolling(65).mean()
    return ma30

def end_price(ticker):
    eprice = pyupbit.get_ohlcv(ticker, "minute30")['close']
    return eprice

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
post_message(myToken, "#getrich", "autotrade start")

while True:
    try:
        now = datetime.datetime.now()
        print(now.second)
        ma30 = get_ma30("KRW-BTC")
        eprice = end_price("KRW-BTC")

        if now.minute == 1 or now.minute == 30:

            if eprice[-1] < ma30[-1]:# and eprice[-1] >= ma30[-1]:
                krw = get_balance("KRW")
                if krw > 5000: #5000이하는 거래되지 않음
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995) #전재산의 0.9995 buy
                    post_message(myToken, "#getrich", "Coin buy : " + str(buy_result))
            elif eprice[-1] > ma30[-1]:# and eprice[-1] < ma30[-1]:
                btc = get_balance("BTC")
                if btc > 0.00008:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                    post_message(myToken, "#getrich", "Coin sell : " + str(sell_result))

        time.sleep(57)

    except Exception as e:
        post_message(myToken,"#getrich", e)
        time.sleep(1)


