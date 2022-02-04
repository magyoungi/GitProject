import pyupbit
import datetime
import time
import requests


upbit = pyupbit.Upbit(access, secret)

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

balance = get_balance("KRW")
print(balance)