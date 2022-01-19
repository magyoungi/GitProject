from slacker import Slacker
import pyupbit
import time
import requests


myToken = "xoxb-2840191596917-2843176437875-EYIvuApqUSPIxwM3MMBwV6UW"
tickers = pyupbit.get_tickers(fiat="KRW")

class Errand:

    def get_market_infos(self, ticker):

        try:
            #"100개의 10분 거래량 갯수의 max 보다 지금의 10분 거래량이 3배가 넘으면 알람"
            past = pyupbit.get_ohlcv(ticker, "minute10")['volume'][-100:-1]
            present = pyupbit.get_ohlcv(ticker, "minute10")['volume'][-1]
            past_price = pyupbit.get_ohlcv(ticker,"minute10")['close'][-2]
            current_price = pyupbit.get_ohlcv(ticker,"minute10")['close'][-1]

            state = None
            if (max(past) * 2.5 < present) and (current_price > past_price):
                response = requests.post("https://slack.com/api/chat.postMessage",
                                         headers={"Authorization": "Bearer " + myToken},
                                         data={"channel": "#개인", "text": ticker + ' ' + str(current_price) + ' ' + str(current_price * 1.03)}
                                         )
            else:
                return None

        except:
            return None

    def main(self):
        while True:
            data1 = {}

            for ticker in tickers:
                data1[ticker] = self.get_market_infos(ticker)
                time.sleep(0.5)


errand = Errand()
errand.main()