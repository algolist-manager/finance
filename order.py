import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from ast import literal_eval
import numpy as np
import matplotlib.pyplot as plt
import krxpricereader
import finance_util
"""
예시 order를 만드는 과정. 원래는 Staregy 클래스에서 나온 order를 사용해야 함.
"""
priceobj = krxpricereader.stockprice_getter()
A066570 = priceobj.get_stock_price('A066570', '20180101', '20190101')
A009150 = priceobj.get_stock_price('A009150', '20180101', '20190101')
data = {'A066570' : A066570, 'A009150' : A009150}
order = pd.DataFrame(index = pd.to_datetime(A066570[0]['trd_dd']))
elec_buy = []
for i in range(1,13):
    for date in order.index[::-1]:
        if date.month == i:
            elec_buy.append(date)
            break
mecha_buy = []
for i in range(1,13):
    for date in order.index:
        if date.month == i:
            mecha_buy.append(date)
            break
order['A066570'] = 0
for idx, day in enumerate(elec_buy):
    order.loc[day, 'A066570'] = idx+1
order['A009150'] = 0
for idx, day in enumerate(mecha_buy):
    order.loc[day, 'A009150'] = idx+1
order.sort_values(['trd_dd'], inplace=True)
order.index.rename('date', inplace = True)





