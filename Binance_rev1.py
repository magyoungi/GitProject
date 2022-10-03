import pyupbit
import datetime
import time
import requests
import pandas as pd
import statistics
import upbit
import numpy as np
import schedule
from binance.client import Client
from binance.enums import *
import math

#binance_rev0 에 short_top8_2_rev0 을 입힘

SlackToken = ""
api_key = ""
secret = ""

client = Client(api_key=api_key, api_secret=secret)

margin = client.get_all_isolated_margin_symbols()
all_Isolated_Margin_Symbol = list(filter(lambda x: x['quote'] == 'USDT' , margin))
df_All_Isolated_Margin_Symbol = pd.DataFrame.from_dict(all_Isolated_Margin_Symbol)
df_All_Isolated_Margin_Symbol = df_All_Isolated_Margin_Symbol.loc[:, 'symbol']
time.sleep(1)

future = client.futures_symbol_ticker()
df_future = pd.DataFrame.from_dict(future)
df_future = df_future.loc[:, 'symbol']
leverage = 10
time.sleep(1)

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
                if ma15() < ma50() and top!= "KRW-BTT" and top!= "KRW-T" and RSI(top)[-3] >= 70 and RSI(top)[-2] < 70 and red_volume(top)*0.5 < blue_volume(top):
                    if top == "KRW-XEC":
                        symbol = "1000" + top.split("-")[1] + "USDT"
                    else:
                        symbol = top.split("-")[1] + "USDT"

                    if symbol in df_future.values:
                        account = client.get_account()
                        balances_USDT = float(list(filter(lambda x: x['asset'] == 'USDT', account['balances']))[0]['free'])
                        transaction = client.futures_account_transfer(asset='USDT', symbol=symbol, amount=balances_USDT,type=1)
                        time.sleep(3)
                        client.futures_change_leverage(symbol=symbol, leverage=leverage)

                        try:
                            client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
                        except:
                            pass
                        time.sleep(1)

                        price = client.futures_symbol_ticker(symbol=symbol)['price']
                        details_BTC = 100 / float(price) * leverage
                        exchange_info = client.futures_exchange_info()['symbols']
                        df_exchange_info = pd.DataFrame.from_dict(exchange_info).set_index('symbol')
                        stepSize = float(df_exchange_info.filters[symbol][2]['stepSize'])
                        Market_buyamount = round(math.floor(details_BTC/ stepSize) * stepSize,int(-1 * math.log10(stepSize)))
                        time.sleep(1)

                        order = client.futures_create_order(
                            symbol=symbol,
                            side='SELL',
                            positionSide='SHORT',
                            type='MARKET',
                            quantity=Market_buyamount,
                            timestamp=None
                        )
                        bprice = pyupbit.get_current_price(top)
                        post_message(SlackToken, "#binance", "Start Future Short : " + top + " " + str(bprice))
                        y = 1
                        while y == 1:
                            nowhour = datetime.datetime.now()
                            time.sleep((5 - nowhour.minute % 5) * 60)
                            cprice = pyupbit.get_current_price(top)
                            if cprice >= 1.015 * bprice:
                                order = client.futures_create_order(
                                    symbol=symbol,
                                    side='BUY',
                                    positionSide='SHORT',
                                    type='MARKET',
                                    quantity=Market_buyamount,
                                    timestamp=None
                                )
                                post_message(SlackToken, "#binance", "Future Short Fail: " + str(cprice))
                                time.sleep(5)
                                futures_account = client.futures_account_balance()
                                df_futures_account = pd.DataFrame.from_dict(futures_account).set_index('asset')
                                details = df_futures_account.loc['USDT']['balance']
                                time.sleep(1)
                                transaction = client.futures_account_transfer(asset="USDT", amount=float(details), type="2")
                                time.sleep(5)
                                break
                            elif cprice <= 0.985 * bprice:
                                order = client.futures_create_order(
                                    symbol=symbol,
                                    side='BUY',
                                    positionSide='SHORT',
                                    type='MARKET',
                                    quantity=Market_buyamount,
                                    timestamp=None
                                )
                                post_message(SlackToken, "#binance", "Future Short Success: " + str(cprice))
                                time.sleep(5)
                                futures_account = client.futures_account_balance()
                                df_futures_account = pd.DataFrame.from_dict(futures_account).set_index('asset')
                                details = df_futures_account.loc['USDT']['balance']
                                time.sleep(1)
                                transaction = client.futures_account_transfer(asset="USDT", amount=float(details), type="2")
                                time.sleep(5)
                                break
                    elif symbol in df_All_Isolated_Margin_Symbol.values:
                        transaction = client.transfer_spot_to_isolated_margin(asset='USDT', symbol=symbol, amount=balances_USDT)
                        asset = top.split("-")[1]
                        time.sleep(3)
                        details_BTC = client.get_max_margin_loan(asset=asset, isolatedSymbol=symbol)
                        avail_Amount_BTC = float(details_BTC['amount'])
                        time.sleep(1)
                        exchange_info = client.get_exchange_info()['symbols']
                        df_exchange_info = pd.DataFrame.from_dict(exchange_info).set_index('symbol')
                        stepSize = float(df_exchange_info.filters[symbol][2]['stepSize'])
                        Market_buyamount = round(math.floor(avail_Amount_BTC * 0.98 / stepSize) * stepSize,int(-1 * math.log10(stepSize)))
                        post_message(SlackToken, "#binance", "So far So good: " + top)

                        order = client.create_margin_order(
                            symbol=symbol,
                            isIsolated='TRUE',
                            side=SIDE_SELL,
                            type=ORDER_TYPE_MARKET,
                            sideEffectType='MARGIN_BUY',
                            quantity=Market_buyamount,
                            timestamp=None
                        )
                        bprice = pyupbit.get_current_price(top)
                        post_message(SlackToken, "#binance", "Start Margin Short : " + top + " " + str(bprice))
                        y = 1
                        while y == 1:
                            nowhour = datetime.datetime.now()
                            time.sleep((5 - nowhour.minute % 5) * 60)
                            cprice = pyupbit.get_current_price(top)
                            if cprice >= 1.015 * bprice:
                                order = client.create_margin_order(
                                    symbol=symbol,
                                    isIsolated='TRUE',
                                    side=SIDE_BUY,
                                    type=ORDER_TYPE_MARKET,
                                    sideEffectType='AUTO_REPAY',
                                    quantity=Market_buyamount,
                                    timestamp=None
                                )
                                post_message(SlackToken, "#binance", "Margin Short Fail: " + str(cprice))
                                time.sleep(5)
                                isolate_Margin_Account = client.get_isolated_margin_account()
                                isolate_Margin_Account_Free = list(filter(lambda x: float(x['quoteAsset']['free']) > 0,isolate_Margin_Account['assets']))
                                for item in isolate_Margin_Account_Free:
                                    try:
                                        transaction = client.transfer_isolated_margin_to_spot(asset='USDT', symbol=item['symbol'],amount=item['quoteAsset']['free'])
                                        time.sleep(1)
                                    except:
                                        post_message(SlackToken, "#binance", "Margin to Spot Transfer Fail: ")
                                time.sleep(1)
                                break
                            elif cprice <= 0.985 * bprice:
                                order = client.create_margin_order(
                                    symbol=symbol,
                                    isIsolated='TRUE',
                                    side=SIDE_BUY,
                                    type=ORDER_TYPE_MARKET,
                                    sideEffectType='AUTO_REPAY',
                                    quantity=Market_buyamount,
                                    timestamp=None
                                )
                                post_message(SlackToken, "#binance", "Margin Short Sucess: " + str(cprice))
                                isolate_Margin_Account = client.get_isolated_margin_account()
                                isolate_Margin_Account_Free = list(filter(lambda x: float(x['quoteAsset']['free']) > 0,isolate_Margin_Account['assets']))
                                for item in isolate_Margin_Account_Free:
                                    try:
                                        transaction = client.transfer_isolated_margin_to_spot(asset='USDT',symbol=item['symbol'],amount=item['quoteAsset']['free'])
                                        time.sleep(1)
                                    except:
                                        post_message(SlackToken, "#binance", "Margin to Spot Transfer Fail: ")
                                time.sleep(1)
                                break
                    else:
                        continue

        except Exception as e:
            post_message(SlackToken, '#binance', e)
            time.sleep(30)

schedule.every(2).minutes.do(main)
post_message(SlackToken, "#binance", "Start!!-----------------------------")
while True:
    schedule.run_pending()
    time.sleep(10)