from slacker import Slacker
import pyupbit
import time
import requests


myToken = "myToken"
tickers = pyupbit.get_tickers(fiat="KRW")
print ("autotrade start")

class Errand:

    def get_market_infos(self, ticker):

        try:
            past = pyupbit.get_ohlcv(ticker, "minute30")['close'][-2]
            present = pyupbit.get_ohlcv(ticker, "minute30")['close'][-1]
            ma65 = present.rolling(65).mean()

            state = None
            if past < ma65 and present >= ma65:
                response = requests.post("https://slack.com/api/chat.postMessage",
                                         headers={"Authorization": "Bearer " + myToken},
                                         data={"channel": "#getrich", "text": 'buy' + ' ' + ticker}
                                         )
            elif past > ma65 and present <= ma65:
                response = requests.post("https://slack.com/api/chat.postMessage",
                                         headers={"Authorization": "Bearer " + myToken},
                                         data={"channel": "#getrich", "text": 'sell' + ' ' + ticker}
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

        time.sleep(1800)


errand = Errand()
errand.main()