import pyupbit
import datetime
import time
import requests
import pandas as pd
import statistics
import upbit
import numpy as np
import schedule

myToken = ""
access = ""
secret = ""
upbit = pyupbit.Upbit(access, secret)

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def macd(top):
    df = pyupbit.get_ohlcv(top, "minute5")
    k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
    d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
    macd = k - d
    return macd

def RSI(top):
    df = pyupbit.get_ohlcv(top, "minute5")

    df['delta'] = df['close'] - df['close'].shift(1)
    df['udelta'] = np.where(df['delta'] >= 0, df['delta'], 0)
    df['ddelta'] = np.where(df['delta'] < 0, df['delta'].abs(), 0)

    df['AU'] = df['udelta'].ewm(alpha=1 / 14, min_periods=14).mean()
    df['AD'] = df['ddelta'].ewm(alpha=1 / 14, min_periods=14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100
    return df['RSI']

def main():
    while True:
        try:
            krw_tickers = pyupbit.get_tickers("KRW")
            url = "https://api.upbit.com/v1/ticker"
            querystring = {"markets": krw_tickers}
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)

            df = pd.DataFrame(response.json())
            df1 = df.sort_values(by='signed_change_rate', ascending=False)
            tops = df1.iloc[0:8]['market']

            for top in tops:
                if top!= "KRW-BTT" and RSI(top)[-2] >= 70:
                    y = 1
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)
                        if RSI(top)[-2] <= 50:
                            while True:
                                if RSI(top)[-3] < RSI(top)[-2]:
                                    break
                            y = 2
                            buy_result = upbit.buy_market_order(top, 8000000)
                            bprice = pyupbit.get_current_price(top)
                            post_message(myToken, "#mool2", "Buy : " + top + " " + str(bprice))
                            while y == 2:
                                nowhour = datetime.datetime.now()
                                time.sleep((5 - nowhour.minute % 5) * 60+180)
                                if RSI(top)[-2] >= 70:
                                    y = 3
                                    while y == 3:
                                        if macd(top)[-2] > macd(top)[-1]:
                                            y = 4
                                            coin = get_balance(top[4:])
                                            sell_result = upbit.sell_market_order(top, coin)
                                            sprice = pyupbit.get_current_price(top)
                                            post_message(myToken, "#mool2", "Sell : " + top + " " + "{:.1f}".format(sprice/bprice*100-100) + "%")
                                            while y == 4:
                                                if RSI(top)[-2] <= 50:
                                                    while True:
                                                        if RSI(top)[-3] < RSI(top)[-2]:
                                                            break
                                                    y = 5
                                                    buy_result = upbit.buy_market_order(top, 8000000)
                                                    bprice = pyupbit.get_current_price(top)
                                                    post_message(myToken, "#mool2", "Buy : " + top + " " + str(bprice))
                                                    while y == 5:
                                                        nowhour = datetime.datetime.now()
                                                        time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                                        if RSI(top)[-2] >= 70:
                                                            y = 6
                                                            while y == 6:
                                                                if macd(top)[-2] > macd(top)[-1]:
                                                                    coin = get_balance(top[4:])
                                                                    sell_result = upbit.sell_market_order(top, coin)
                                                                    sprice = pyupbit.get_current_price(top)
                                                                    post_message(myToken, "#mool2","Sell : " + top + " " + "{:.1f}".format(sprice / bprice * 100 - 100) + "%")
                                                                    break
                                                        elif RSI(top)[-3] >= 30 and RSI(top)[-2] < 30:
                                                            y = 6
                                                            past = pyupbit.get_ohlcv(top, "minute5")['volume'][-5:-2]
                                                            present = pyupbit.get_ohlcv(top, "minute5")['volume'][-2]
                                                            avg = sum(past) / len(past)
                                                            if present >= avg * 3:
                                                                while y == 6:
                                                                    nowhour = datetime.datetime.now()
                                                                    time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                                                    if RSI(top)[-2] >= 50:
                                                                        coin = get_balance(top[4:])
                                                                        sell_result = upbit.sell_market_order(top, coin)
                                                                        sprice = pyupbit.get_current_price(top)
                                                                        post_message(myToken, "#mool2", "Sell : " + top + " " + "{:.1f}".format(sprice / nbprice * 100 - 100) + "%")
                                                                        break
                                                            elif present < avg * 3:
                                                                while == 6:
                                                                    nowhour = datetime.datetime.now()
                                                                    time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                                                    if RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                                                                        buy_result = upbit.buy_market_order(top, 12000000)
                                                                        nprice = pyupbit.get_current_price(top)
                                                                        nbprice = (bprice + nprice) / 2
                                                                        post_message(myToken, "#mool2","Extra Buy : " + top + " " + str(nbprice))
                                                                        while y == 6:
                                                                            nowhour = datetime.datetime.now()
                                                                            time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                                                            if RSI(top)[-2] >= 50:
                                                                                coin = get_balance(top[4:])
                                                                                sell_result = upbit.sell_market_order(top, coin)
                                                                                sprice = pyupbit.get_current_price(top)
                                                                                post_message(myToken, "#mool2","Sell : " + top + " " + "{:.1f}".format(sprice / nbprice * 100 - 100) + "%")
                                                                                break
                                                                        break
                                elif RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                                    y = 3
                                    past = pyupbit.get_ohlcv(top, "minute5")['volume'][-5:-2]
                                    present = pyupbit.get_ohlcv(top, "minute5")['volume'][-2]
                                    avg = sum(past) / len(past)
                                    if present >= avg * 3:
                                        while y == 3:
                                            nowhour = datetime.datetime.now()
                                            time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                            if RSI(top)[-2] >= 50:
                                                coin = get_balance(top[4:])
                                                sell_result = upbit.sell_market_order(top, coin)
                                                sprice = pyupbit.get_current_price(top)
                                                post_message(myToken, "#mool2", "Sell : " + top + " " + "{:.1f}".format(sprice / nbprice * 100 - 100) + "%")
                                                break
                                    elif present < avg * 3:
                                        while y == 3:
                                            nowhour = datetime.datetime.now()
                                            time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                            if RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                                                buy_result = upbit.buy_market_order(top, 12000000)
                                                nprice = pyupbit.get_current_price(top)
                                                nbprice = (bprice + nprice) / 2
                                                post_message(myToken, "#mool2","Extra Buy : " + top + " " + str(nbprice))
                                                while y == 6:
                                                    nowhour = datetime.datetime.now()
                                                    time.sleep((5 - nowhour.minute % 5) * 60 + 180)
                                                    if RSI(top)[-2] >= 50:
                                                        coin = get_balance(top[4:])
                                                        sell_result = upbit.sell_market_order(top, coin)
                                                        sprice = pyupbit.get_current_price(top)
                                                        post_message(myToken, "#mool2", "Sell : " + top + " " + "{:.1f}".format(sprice / nbprice * 100 - 100) + "%")
                                                        break
                                                break

        except Exception as e:
            post_message(myToken, '#mool2', e)
            time.sleep(30)

schedule.every(2).minutes.do(main)
post_message(myToken, "#mool2", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)
