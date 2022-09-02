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

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

def macd(top):
    df = pyupbit.get_ohlcv(top, "minute5")
    k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
    d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
    macd = k - d
    return macd

def macd_y(top):
    df = pyupbit.get_ohlcv(top, "minute5")
    k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
    d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
    macd = k - d
    macd_y = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    return macd_y

def ma15():
    df =  pyupbit.get_ohlcv("KRW-BTC", "minute5")['close']
    df15 = df[-15:]
    ma15 = sum(df15) / len(df15)
    return ma15

def ma50():
    df =  pyupbit.get_ohlcv("KRW-BTC", "minute5")['close']
    df50 = df[-50:]
    ma50 = sum(df50) / len(df50)
    return ma50

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
                if top!= "KRW-BTT" and RSI(top)[-2] <= 30 and RSI(top)[-1] > 30:
                    y = 1
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)
                        past = RSI(top)[-5:-2]
                        past2 = RSI(top)[-4:-1]
                        avg = sum(past) / len(past)
                        avg2 = sum(past2) / len(past2)
                        if avg < avg2:
                            break
                    bprice = pyupbit.get_current_price(top)
                    post_message(myToken, "#top8_beta", "Start Long : " + top + " " + str(bprice))
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)
                        cprice = pyupbit.get_current_price(top)
                        if cprice >= 1.01 * bprice:
                            post_message(myToken, "#top8_beta", "Long Sucess: " + str(cprice))
                            break
                        elif cprice <= 0.985 * bprice:
                            post_message(myToken, "#top8_beta", "Long Fail: " + str(cprice))
                            break

                elif top!= "KRW-BTT" and RSI(top)[-2] < 70 and RSI(top)[-1] >= 70 and ma15() < ma50():
                    y = 1
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)
                        past = RSI(top)[-5:-2]
                        past2 = RSI(top)[-4:-1]
                        avg = sum(past) / len(past)
                        avg2 = sum(past2) / len(past2)
                        if avg > avg2:
                            break
                    bprice = pyupbit.get_current_price(top)
                    post_message(myToken, "#top8_beta", "Start Short : " + top + " " + str(bprice))
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)
                        cprice = pyupbit.get_current_price(top)
                        if cprice >= 1.015 * bprice:
                            post_message(myToken, "#top8_beta", "Short Fail: " + str(cprice))
                            break
                        elif cprice <= 0.985 * bprice:
                            post_message(myToken, "#top8_beta", "Short Sucess: " + str(cprice))
                            break
        except Exception as e:
            post_message(myToken, '#top8_beta', e)
            time.sleep(30)

schedule.every(2).minutes.do(main)
post_message(myToken, "#top8_beta", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)