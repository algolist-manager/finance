import krxcomreader
import krxcodereader
import krxindexreader
import krxpricereader

import investingreader

import pandas as pd
from datetime import datetime
"""
모든 datareader들을 모아서 원하는 데이터를 쉽게 추출할 수 있게 도와주는 클래스
"""

class datamanager():
    def __init__(self):
        self.today = datetime.today().strftime('%Y%m%d')
        self.full_code = pd.read_pickle('../Database/full_code.pickle')
        self.adj_total = pd.read_pickle('../Database/adj_total.pickle')
        self.price_data = pd.read_pickle('../Database/10year.pickle')
        self.krxholidays = pd.read_pickle('../Database/krxholidays.pickle')
        self.krxbizdays = pd.read_pickle('../Database/krxbiz.pickle')





# 1. 1년간 삼성전자라는 기업의 OHLCA 데이터
# 2. 가지고 있는 전 종목의 OHLCA 데이터
# 3. 전 종목 code와 종목만 있는 데이터