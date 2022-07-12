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
            tops = df1.iloc[0:40]['market']

            for top in tops:

                if RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                    bprice = pyupbit.get_current_price(top)
                    post_message(myToken, "#test", "Buy : " + top + " " + str(bprice))
                    y = 1
                    while y == 1:
                        nowhour = datetime.datetime.now()
                        time.sleep((5 - nowhour.minute % 5) * 60)

                        if RSI(top)[-3] <= 70 and RSI(top)[-2] > 70:
                            sprice = pyupbit.get_current_price(top)
                            post_message(myToken, "#test", "Sell : " + top + " " + "{:.1f}".format(sprice/bprice*100-100) + "%")
                            break
                        elif RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                            y = 2
                            nprice = pyupbit.get_current_price(top)
                            nbprice = (bprice+nprice)/y
                            post_message(myToken, "#test", "Extra Buy : " + top + " " + str(nbprice))

                            while y == 2:
                                nowhour = datetime.datetime.now()
                                time.sleep((5 - nowhour.minute % 5) * 60)

                                if RSI(top)[-3] <= 70 and RSI(top)[-2] > 70:
                                    sprice = pyupbit.get_current_price(top)
                                    post_message(myToken, "#test", "Sell : " + top + " " + "{:.1f}".format(sprice/nbprice*100-100) + "%")
                                    break
                                elif RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                                    y = 3
                                    nprice = pyupbit.get_current_price(top)
                                    nbprice = (nbprice + nprice) / 2
                                    post_message(myToken, "#test", "Extra Buy : " + top + " " + str(nbprice))

                                    while y == 3:
                                        nowhour = datetime.datetime.now()
                                        time.sleep((5 - nowhour.minute % 5) * 60)

                                        if RSI(top)[-3] <= 70 and RSI(top)[-2] > 70:
                                            sprice = pyupbit.get_current_price(top)
                                            post_message(myToken, "#test", "Sell : " + top + " " + "{:.1f}".format(sprice/nbprice * 100 - 100) + "%")
                                            break
                                        elif RSI(top)[-3] <= 30 and RSI(top)[-2] > 30:
                                            y = 4
                                            nprice = pyupbit.get_current_price(top)
                                            nbprice = (nbprice + nprice) / 2
                                            post_message(myToken, "#test", "Extra Buy : " + top + " " + str(nbprice))

                                            while y == 4:
                                                nowhour = datetime.datetime.now()
                                                time.sleep((5 - nowhour.minute % 5) * 60)

                                                if RSI(top)[-3] <= 70 and RSI(top)[-2] > 70:
                                                    sprice = pyupbit.get_current_price(top)
                                                    post_message(myToken, "#test","Sell : " + top + " " + "{:.1f}".format(sprice / nbprice * 100 - 100) + "%")
                                                    break
                                                elif RSI(top)[-3] <= 30:
                                                    sprice = pyupbit.get_current_price(top)
                                                    post_message(myToken, "#test", "Kill : " + top + " " + "{:.1f}".format(sprice / nbprice * 100 - 100) + "%")
                                                    break



        except Exception as e:
            post_message(myToken, '#test', e)
            time.sleep(30)

schedule.every(2).minutes.do(main)
post_message(myToken, "#test", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)
