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
    n=1
    while n == 1:
        try:
            krw_tickers = pyupbit.get_tickers("KRW")
            url = "https://api.upbit.com/v1/ticker"
            querystring = {"markets": krw_tickers}
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)

            df = pd.DataFrame(response.json())
            df1 = df.sort_values(by='signed_change_rate', ascending=False)
            tops = df1.iloc[0:100]['market']

            for top in tops:
                pd.set_option('display.float_format', lambda x: '%.2f' % x)
                df = pyupbit.get_ohlcv(top, "minute5")

                df['delta'] = df['close'] - df['close'].shift(1)
                df['udelta'] = np.where(df['delta'] >= 0, df['delta'], 0)
                df['ddelta'] = np.where(df['delta'] < 0, df['delta'].abs(), 0)

                df['AU'] = df['udelta'].ewm(alpha=1 / 9, min_periods=9).mean()
                df['AD'] = df['ddelta'].ewm(alpha=1 / 9, min_periods=9).mean()
                df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100

                if df['RSI'][-1] <= 30:
                    bprice = pyupbit.get_current_price(top)
                    post_message(myToken, "#test", "Buy : " + top + " " + str(bprice) + " " + str(n))
                n += 1

        except Exception as e:
            post_message(myToken, '#test', e)
            time.sleep(30)

schedule.every().day.at("08:57").do(go)
post_message(myToken, "#test", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(1)
