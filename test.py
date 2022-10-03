import pyupbit
import datetime
import time
import requests
import pandas as pd
import statistics
import upbit
import numpy as np
import schedule
import ccxt
from binance.client import Client
from binance.enums import *
import math


client = Client(api_key=api_key, api_secret=secret)

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )

while True:
    try:
        transaction = client.futures_account_transfer(asset='USDT', symbol="BTCUSDT", amount=10,type=1)
        post_message(SlackToken, "#binance", "transfer complete")
        time.sleep(300)

    except Exception as e:
        post_message(myToken, '#binance', e)
        time.sleep(300)

