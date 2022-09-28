import pyupbit
import datetime
import time
import requests
import pandas as pd
import statistics
import upbit
import numpy as np
import schedule
#short_top8_2에서 70하향한 현재 거래량이 과거 3개 양봉 거래량의 0.5 이상일 때
myToken = ""

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

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

def red_volume(top):
    open = pyupbit.get_ohlcv(top, "minute5")['open']
    close = pyupbit.get_ohlcv(top, "minute5")['close']
    df = pyupbit.get_ohlcv(top, "minute5")['volume']
    max = df[-4]
    index = -4
    for i in range(-4, -1): #-6 부터 -2까지
        if df[i] > max and open[i] < close[i]: #하나 전 거래량 보다 현 거래량이 크고 동시에 양봉일 때만 if 문구 들어감
            max = df[i]
            index = i
    return df[index]

def blue_volume(top):
    df = pyupbit.get_ohlcv(top, "minute5")['volume'][-1]
    return df

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
                if top!= "KRW-BTT" and top!= "KRW-T" and RSI(top)[-3] >= 70 and RSI(top)[-2] < 70 and red_volume(top)*0.5 < blue_volume(top):
                    if ma15() < ma50():
                        bprice = pyupbit.get_current_price(top)
                        post_message(myToken, "#top8_beta2_rev0", "Start Short : " + top + " " + str(bprice))
                        y = 1
                        while y == 1:
                            nowhour = datetime.datetime.now()
                            time.sleep((5 - nowhour.minute % 5) * 60)
                            cprice = pyupbit.get_current_price(top)
                            if cprice >= 1.015 * bprice:
                                post_message(myToken, "#top8_beta2_rev0", "Short Fail: " + str(cprice))
                                break
                            elif cprice <= 0.985 * bprice:
                                post_message(myToken, "#top8_beta2_rev0", "Short Sucess: " + str(cprice))
                                break
                    elif ma15() > ma50():
                        bprice = pyupbit.get_current_price(top)
                        post_message(myToken, "#top8_beta2_rev0", "OMG Start Short : " + top + " " + str(bprice))
                        y = 1
                        while y == 1:
                            nowhour = datetime.datetime.now()
                            time.sleep((5 - nowhour.minute % 5) * 60)
                            cprice = pyupbit.get_current_price(top)
                            if cprice >= 1.015 * bprice:
                                post_message(myToken, "#top8_beta2_rev0", "Told ya Short Fail: " + str(cprice))
                                break
                            elif cprice <= 0.985 * bprice:
                                post_message(myToken, "#top8_beta2_rev0", "OMG Short Sucess: " + str(cprice))
                                break

        except Exception as e:
            post_message(myToken, '#top8_beta2_rev0', e)
            time.sleep(30)

schedule.every(2).minutes.do(main)
post_message(myToken, "#top8_beta2_rev0", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)