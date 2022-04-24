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
def go():
    pasts = pd.Series(dtype='float64')

    while True:
        try:
            krw_tickers = pyupbit.get_tickers("KRW")
            url = "https://api.upbit.com/v1/ticker"
            querystring = {"markets": krw_tickers}
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)

            df = pd.DataFrame(response.json())
            df1 = df.sort_values(by='signed_change_rate', ascending=False)
            tops = df1.iloc[0:20]['market']
            n = 1

            for top in tops:
                if top in pd.unique(pasts):
                    None
                elif top!= "KRW-STPT" and top != "KRW-CRE":
                    past = pyupbit.get_ohlcv(top, "minute5")['volume'][-27:-3]
                    now = pyupbit.get_ohlcv(top, "minute5")['volume'][-2]
                    ppc = pyupbit.get_ohlcv(top, "minute5")['close'][-2]
                    ppo = pyupbit.get_ohlcv(top, "minute5")['open'][-2]

                    if (statistics.mean(past) * 2.5 <= now) and ppo < ppc:
                        pasts = pasts.append(pd.Series([top]))
                    elif (statistics.mean(past) * 2.5 <= now) and ppo > ppc:
                        time.sleep(300)
                        ppc = pyupbit.get_ohlcv(top, "minute5")['close'][-2]
                        ppo = pyupbit.get_ohlcv(top, "minute5")['open'][-2]
                        while ppo > ppc:
                            time.sleep(300)
                            ppc = pyupbit.get_ohlcv(top, "minute5")['close'][-2]
                            ppo = pyupbit.get_ohlcv(top, "minute5")['open'][-2]
                        bprice = pyupbit.get_current_price(top)
                        post_message(myToken, "#joopjoop", "Coin Buy:" + top + " " + str(bprice))
                        pasts = pasts.append(pd.Series([top]))
                        while True:
                            cprice = pyupbit.get_current_price(top)
                            if cprice >= 1.02 * bprice:
                                post_message(myToken, "#joopjoop", "Success JoopJoop: " + top)
                                break
                            elif cprice <= 0.98 * bprice:
                                post_message(myToken, "#joopjoop", "Fail JoopJoop: " + top)
                                break

            now = datetime.datetime.now()
            if now.hour == 23 and now.minute > 53:
                break
            else:
                time.sleep((5-now.minute%5)*60-now.second)
        except Exception as e:
            post_message(myToken, '#rich', e)
            time.sleep(5)

schedule.every(5).minutes.do(go)

while True:
    schedule.run_pending()
    time.sleep(10)