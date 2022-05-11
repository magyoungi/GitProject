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
            tops = df1.iloc[0:15]['market']
            n = 1

            for top in tops:
                if top in pd.unique(pasts):
                    None
                elif top!= "KRW-STPT" and top!= "KRW-CRE" and top!= "KRW-BTT" and top!= "KRW-T":
                    past = pyupbit.get_ohlcv(top, "minute5")['volume'][-26:-2]
                    past1 = pyupbit.get_ohlcv(top, "minute5")['volume'][-26:-3]
                    now = pyupbit.get_ohlcv(top, "minute5")['volume'][-1]
                    now2 = pyupbit.get_ohlcv(top, "minute5")['volume'][-2]
                    ppc = pyupbit.get_ohlcv(top, "minute5")['close'][-1]
                    ppo = pyupbit.get_ohlcv(top, "minute5")['open'][-1]

                    if (statistics.mean(past) * 2.5 <= now) and (statistics.mean(past1) * 1.5 >= now2) and max(past1)<(statistics.mean(past1)*3.5) and (ppc-ppo)/ppo < 0.08 and (ppc-ppo)/ppo > 0.01:
                        bprice = pyupbit.get_current_price(top)
                        post_message(myToken, "#test", "Buy: " + top + " " + str(bprice) + " " + str(n))
                        pasts = pasts.append(pd.Series([top]))
                        now3 = datetime.datetime.now()
                        nowhour = now3.hour
                        time.sleep((5-now3.minute%5)*60-now3.second+300) #사고 난 다다음 5분봉 시작 할 때
                        newppc = pyupbit.get_ohlcv(top, "minute5")['close'][-2]
                        newppo = pyupbit.get_ohlcv(top, "minute5")['open'][-2]

                        if newppc < newppo: #만약 빨간 봉 다음 파란 퐁이면 2% 떨어지면 판다. 물타기 없음
                            while True:
                                newhour = datetime.datetime.now().hour
                                time.sleep(2)
                                if newhour != (nowhour + 12) or newhour != (nowhour - 12):
                                    cprice = pyupbit.get_current_price(top)
                                    if cprice >= 1.02 * bprice:
                                        post_message(myToken, "#test", "Success High +2%: " + top + " " + str(cprice))
                                        break
                                    elif cprice <= 0.99 * bprice:
                                        post_message(myToken, "#test", "Fail Low -1%: " + top + " " + str(cprice))
                                        break
                                else:
                                    post_message(myToken, "#test", "Trade Null")
                                    break

                        elif newppc >= newppo: #만약 빨간 봉 다음 빨간 봉이면
                            while True:
                                newhour = datetime.datetime.now().hour
                                time.sleep(2)
                                if newhour != (nowhour + 12) or  newhour != (nowhour - 12):
                                    cprice = pyupbit.get_current_price(top)
                                    if cprice >= 1.02 * bprice:
                                        now4 = datetime.datetime.now()
                                        time.sleep(60-now4.second+65)
                                        bbc = pyupbit.get_ohlcv(top, "minute1")['close'][-2]
                                        bbo = pyupbit.get_ohlcv(top, "minute1")['open'][-2]
                                        while bbo > bbc:
                                            time.sleep(60)
                                            bbc = pyupbit.get_ohlcv(top, "minute1")['close'][-2]
                                            bbo = pyupbit.get_ohlcv(top, "minute1")['open'][-2]
                                        cprice = pyupbit.get_current_price(top)
                                        post_message(myToken, "#test", "Red Success High: " + str(cprice/bprice-1) + "%" + top)
                                        break
                                    elif cprice <= 0.98 * bprice:
                                        nbprice = (cprice+bprice)/2
                                        while True:
                                            time.sleep(2)
                                            ncprice = pyupbit.get_current_price(top)
                                            if ncprice >= 1.01 * nbprice:
                                                post_message(myToken, "#test", "Success Low 2%: " + top + " " + str(ncprice))
                                                break
                                            elif ncprice <= 0.99 * nbprice:
                                                post_message(myToken, "#test", "Mooltagi Fail -2% : " + top + " " + str(cprice))
                                                break
                                        break
                                else:
                                    post_message(myToken, "#test", "Trade Null")
                                    break


                n += 1

            now = datetime.datetime.now()
            if now.hour >57 and now.minute <= 59:
                break
            else:
                time.sleep(60-now.second)
        except Exception as e:
            post_message(myToken, '#test', e)
            time.sleep(30)

schedule.every(2).minutes.do(go)
post_message(myToken, "#test", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)