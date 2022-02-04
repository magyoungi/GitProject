import pyupbit
import datetime
import time
import requests

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

        if now.second == 1 or now.second == 30:

            if eprice[-1] < ma30[-1]:# and eprice[-1] >= ma30[-1]:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken, "#getrich", "Coin buy : " + str(buy_result))
            elif eprice[-1] > ma30[-1]:
                btc = get_balance("BTC")
                if btc > 0.00008:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                    post_message(myToken, "#getrich", "Coin sell : " + str(sell_result))

        time.sleep(1)

    except Exception as e:
        post_message(myToken,"#getrich", e)
        time.sleep(1)


