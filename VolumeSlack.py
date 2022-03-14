import pyupbit
import datetime
import time
import requests
import pandas as pd
import statistics

myToken = ""

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

print("autotrade start")
post_message(myToken, "#rich", "autotrade start")

while True:
    try:
        krw_tickers = pyupbit.get_tickers("KRW")
        url = "https://api.upbit.com/v1/ticker"
        querystring = {"markets": krw_tickers}
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers, params=querystring)

        df = pd.DataFrame(response.json())
        df1 = df.sort_values(by='signed_change_rate', ascending=False)
        tops = df1.iloc[0:11]['market']

        for top in tops:
            past = pyupbit.get_ohlcv(top, "minute5")['volume'][-30:-1]
            present = pyupbit.get_ohlcv(top, "minute5")['volume'][-1]
            past_price = pyupbit.get_ohlcv(top, "minute5")['close'][-2]
            current_price = pyupbit.get_ohlcv(top, "minute5")['close'][-1]

            if (statistics.mean(past) * 6 <= present) and (current_price > past_price):
                krw = get_balance("KRW")
                if krw > 5000:
                    bprice = pyupbit.get_current_price(top)
                    post_message(myToken, "#rich", "Coin buy : " + top + bprice)

        time.sleep(300)

    except Exception as e:
        post_message(myToken,"#rich", e)
        time.sleep(30)


