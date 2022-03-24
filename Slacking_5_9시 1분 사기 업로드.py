import pyupbit
import datetime
import time
import requests
import pandas as pd

access = "
secret = "

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

while True:
    try:
        now = datetime.datetime.now()
        if now.hour == 9 and now.minute == 1:

            krw_tickers = pyupbit.get_tickers("KRW")
            url = "https://api.upbit.com/v1/ticker"
            querystring = {"markets": krw_tickers}
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)

            df = pd.DataFrame(response.json())
            df1 = df.sort_values(by='signed_change_rate', ascending=False)
            tops = df1.iloc[0:3]['market']

            for top in tops:
                bprice = pyupbit.get_current_price(top)
                buy_result = upbit.buy_market_order(top, 10000000)

        time.sleep(60)

    except Exception as e:
        time.sleep(30)


