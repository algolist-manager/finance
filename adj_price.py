import pandas as pd
import datetime
import win32com.client
import requests
from bs4 import BeautifulSoup as bs
import time
import json
import multiprocessing


def get_df_cur():
    url = 'https://www.investing.com/stock-screener/Service/SearchStocks'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest'
    }
    payload = {
        'country[]': '11',
        'sector': '7,5,12,3,8,9,1,6,2,4,10,11',
        'industry': '81,56,59,41,68,67,88,51,72,47,12,8,50,2,71,9,69,45,46,13,94,102,95,58,100,101,87,31,6,38,79,30,77,28,5,60,18,26,44,35,53,48,49,55,78,7,86,10,1,34,3,11,62,16,24,20,54,33,83,29,76,37,90,85,82,22,14,17,19,43,89,96,57,84,93,27,74,97,4,73,36,42,98,65,70,40,99,39,92,75,66,63,21,25,64,61,32,91,52,23,15,80',
        'equityType': 'ORD,DRC,Preferred,Unit,ClosedEnd,REIT,ELKS,OpenEnd,Right,ParticipationShare,CapitalSecurity,PerpetualCapitalSecurity,GuaranteeCertificate,IGC,Warrant,SeniorNote,Debenture,ETF,ADR,ETC,ETN',
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


def get_raw_data(short_code, st_date, end_date):
    num_code = short_code[1:]
    # df_curr = get_df_cur()
    curr_id = str(df_curr[df_curr['num_code'] == num_code].iloc[0, 0])
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://www.investing.com/instruments/HistoricalDataAjax'
    payload = {
        'interval_sec': 'Daily',
        'sort_col': 'date',
        'sort_ord': 'DESC',
        'action': 'historical_data'
    }

    def tr_date(date):
        year, month, day = date[:4], date[4:6], date[6:]
        tr_date = month + '/' + day + '/' + year
        return tr_date

    payload['curr_id'] = curr_id
    payload['header'] = num_code + ' ' + 'Historical Data'
    payload['st_date'] = tr_date(st_date)
    payload['end_date'] = tr_date(end_date)

    r1 = requests.post(url, data=payload, headers=header)
    tables = bs(r1.text, 'lxml').findAll('table')
    raw_data = pd.read_html(str(tables[0]))[0]
    return raw_data


def preprocess(short_code, raw_data):
    # columns 정리
    raw_data.drop(['Open', 'High', 'Low', 'Vol.', 'Change %'], axis='columns', inplace=True)
    raw_data.rename(columns={'Date': 'date', 'Price': 'adj'}, inplace=True)
    raw_data['short_code'] = short_code

    def tr_date_1(date_1):
        tr_month = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12
        }
        year, month, day = int(date_1[-4:]), tr_month[date_1[:3]], int(date_1[4:6])
        tr_date_var = datetime.date(year, month, day)
        return tr_date_var

    raw_data['date'] = raw_data['date'].apply(lambda x: tr_date_1(x))
    fined_data = raw_data
    return fined_data


def get_adj_stock(short_code):
    raw_data = get_raw_data(short_code, '20180122', '20200120')
    fined_data = preprocess(short_code, raw_data)
    return fined_data


if __name__ == "__main__":
    start_time = time.time()
    all_total = pd.read_pickle('./all_total.pickle')
    codes = all_total['short_code'].unique()

    pool = multiprocessing.Pool(8)
    adj_list = pool.map(get_adj_stock, codes)
    adj_total = pd.concat(adj_list)
    new_all_total = pd.merge(all_total, adj_total, on=['date', 'short_code'])

    end_time = time.time()
    print('소요시간 : {}초'.format(end_time - start_time))


## investing.com에 없는 기업의 주식이 있다. 따라서 회귀분석을 할 때 수정주가가 있으면 수정주가를 쓰고, 없으면 종가를 쓴다.