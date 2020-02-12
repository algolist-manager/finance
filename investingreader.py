import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import json
import finance_util


class investingreader():
    def __init__(self):
        self.url = 'https://www.investing.com/stock-screener/Service/SearchStocks'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.117 Safari/537.36',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }

        self.df_curr = pd.read_pickle('../Database/df_curr.pickle')

    def get_df_curr(self):
        url = self.url
        header = self.header
        payload = {
            'country[]': '11',
            'sector': '7,5,12,3,8,9,1,6,2,4,10,11',
            'industry': '81,56,59,41,68,67,88,51,72,47,12,8,50,2,71,9,69,45,46,13,94,102,95,58,100,101,87,31,6,38,79,'
                        '30,77,28,5,60,18,26,44,35,53,48,49,55,78,7,86,10,1,34,3,11,62,16,24,20,54,33,83,29,76,37,90,'
                        '85,82,22,14,17,19,43,89,96,57,84,93,27,74,97,4,73,36,42,98,65,70,40,99,39,92,75,66,63,21,25,'
                        '64,61,32,91,52,23,15,80',
            'equityType': 'ORD,DRC,Preferred,Unit,ClosedEnd,REIT,ELKS,OpenEnd,Right,ParticipationShare,'
                          'CapitalSecurity,PerpetualCapitalSecurity,GuaranteeCertificate,IGC,Warrant,SeniorNote,'
                          'Debenture,ETF,ADR,ETC,ETN',
            'pn': '1',
            'order[col]': 'eq_market_cap',
            'order[dir]': 'd',
        }
        df_curr = pd.DataFrame()
        for i in range(1, 49):  # 2373 / 50 = 47.46
            print(i)
            payload['pn'] = i
            r = requests.post(url, data=payload, headers=header)
            dat = pd.DataFrame(json.loads(r.text)['hits'])[['pair_ID', 'stock_symbol']]
            df_curr = pd.concat([df_curr, dat])

        df_curr.columns = ['curr_id', 'num_code']
        return df_curr

    def get_adj_price(self, short_code, fromdate, todate):
        num_code = short_code[1:]
        df_curr = self.df_curr
        curr_id = str(df_curr[df_curr['num_code'] == num_code].iloc[0, 0])
        header = self.header
        url = 'https://www.investing.com/instruments/HistoricalDataAjax'
        payload = {'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data',
                   'curr_id': curr_id, 'header': num_code + ' ' + 'Historical Data',
                   'st_date': finance_util.tr_date(fromdate), 'end_date': finance_util.tr_date(todate)}

        r = requests.post(url, data=payload, headers=header)
        tables = bs(r.text, 'lxml').findAll('table')
        raw_data = pd.read_html(str(tables[0]))[0]
        return raw_data

    def preprocess(self, short_code, raw_data):
        # columns 정리
        raw_data.drop(['Open', 'High', 'Low', 'Vol.', 'Change %'], axis='columns', inplace=True)
        raw_data.rename(columns={'Date': 'date', 'Price': 'adj'}, inplace=True)
        raw_data['short_code'] = short_code

        raw_data['date'] = raw_data['date'].apply(lambda x: finance_util.tr_date_1(x))
        fined_data = raw_data
        return fined_data

    def get_adj_stock(self, short_code, fromdate, todate):
        raw_data = self.get_adj_price(short_code, fromdate, todate)
        fined_data = self.preprocess(short_code, raw_data)
        return fined_data

## investing.com에 없는 기업의 주식이 있다. 따라서 회귀분석을 할 때 수정주가가 있으면 수정주가를 쓰고, 없으면 종가를 쓴다.
