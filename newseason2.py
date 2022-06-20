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
    while True:
        try:
            krw_tickers = pyupbit.get_tickers("KRW")
            url = "https://api.upbit.com/v1/ticker"
            querystring = {"markets": krw_tickers}
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)

            df = pd.DataFrame(response.json())
            df1 = df.sort_values(by='signed_change_rate', ascending=False)
            tops = df1.iloc[0:15]['market']

            for top in tops:
                pd.set_option('display.float_format', lambda x: '%.2f' % x)
                df = pyupbit.get_ohlcv(top, "minute5")

                df['delta'] = df['close'] - df['close'].shift(1)
                df['udelta'] = np.where(df['delta'] >= 0, df['delta'], 0)
                df['ddelta'] = np.where(df['delta'] < 0, df['delta'].abs(), 0)

                df['AU'] = df['udelta'].ewm(alpha=1 / 14, min_periods=14).mean()
                df['AD'] = df['ddelta'].ewm(alpha=1 / 14, min_periods=14).mean()
                df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100

                if df['RSI'][-3] <= 30 and df['RSI'][-2] > 30:
                    y = 1
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)

                        df = pyupbit.get_ohlcv(top, "minute5")
                        k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
                        d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
                        macd = k - d
                        macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()

                        if macd[-2] > macd_s[-2]:
                            y = 0
                            bprice = pyupbit.get_current_price(top)
                            post_message(myToken, "#rich", "Buy : " + top + " " + str(bprice))
                            while True:
                                nowhour = datetime.datetime.now()
                                time.sleep((5 - nowhour.minute % 5) * 60)

                                df = pyupbit.get_ohlcv(top, "minute5")
                                k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
                                d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
                                macd = k - d
                                macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()

                                if macd_s[-2] > macd[-2]:
                                    sprice = pyupbit.get_current_price(top)
                                    post_message(myToken, "#rich", "Sell : " + top + " " + "{:.1f}".format(sprice/bprice*100-100) + "%")
                                    break

        except Exception as e:
            post_message(myToken, '#rich', e)
            time.sleep(30)

schedule.every(2).minutes.do(go)
post_message(myToken, "#rich", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)
