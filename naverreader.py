import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from datamanager import datamanager
from finance_util import link_list
from datetime import datetime
import time

class naverreader():
    def __init__(self):
        self.mg = datamanager()
        self.companies = pd.read_pickle('../Database/naver_companies.pickle')

    def get_adj_naver_list(self, num_code, count):
        # num_code = '005930'
        # count = 500 -> 실제 거래일 수와 달라서 to_date가 0이 아닐 수 있다. 그리고 시작 시점을 조절하지 못함.
        url = 'https://fchart.stock.naver.com/sise.nhn'
        payload = {
            'symbol': num_code,
            'timeframe': 'day',
            'count': count,
            'requestType': 0
        }
        req = requests.get(url, params=payload).text
        soup = bs(req, 'lxml')
        row_list = []
        for item in soup.findAll('item'):
            row = item['data'].split('|')
            row.append('A' + num_code)
            row_list.append(row)

        return row_list

    def get_naver_companies(self):
        """
        naver는
        """
        url = 'https://finance.naver.com/sise/sise_market_sum.nhn'
        payload = dict()
        company_pages = []
        for j in [0, 1]:  # 0은 코스피, 1은 코스닥
            for i in range(1, 33):
                payload['sosok'] = j
                payload['page'] = i
                req = requests.get(url, params=payload).text
                company_pages.append(pd.read_html(req)[1])

        df = pd.concat(company_pages)
        codenames = df['종목명']
        codenames.columns = ['codeName']
        codenames.dropna(inplace=True)
        codenames.reset_index(drop=True, inplace=True)

        codenames_df = pd.DataFrame(codenames)
        companies = codenames_df.merge(self.mg.full_code, on=['codeName'])
        return companies

    def get_naver_total(self, days): # 여기서 얻은 데이터는 관리 종목인 경우 값이 0이다.
        super_list = []
        for i, code in enumerate(self.companies['short_code']):
            try:
                short_code = code
                print(code)
                num_code = short_code[1:]
                super_list.append(self.get_adj_naver_list(num_code, count=days))
                if i==3: break
            except KeyError:
                pass

        linked = pd.DataFrame(link_list(super_list))
        linked.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'short_code']
        linked['date'] = linked['date'].apply(lambda x: pd.to_datetime(x))
        linked[['open', 'high', 'low', 'close', 'volume']] = linked[
            ['open', 'high', 'low', 'close', 'volume']].applymap(lambda x: int(x))
        linked.set_index('date', inplace=True)

        return linked

    def get_current_price(self):
        url = 'https://finance.naver.com/sise/field_submit.nhn?menu=market_sum&returnUrl=http%3A%2F%2Ffinance.naver' \
              '.com%2Fsise%2Fsise_market_sum.nhn%3F%26page%3D1&fieldIds=quant&fieldIds=open_val&fieldIds=high_val' \
              '&fieldIds=low_val '
        payload = dict()
        company_pages = []
        for sosok in [0, 1]:  # 0은 코스피, 1은 코스닥
            payload['sosok'] = sosok
            for page_num in range(1, 33):  # 마지막 페이지는 거의 33
                print('페이지 수 : {}'.format(page_num))
                payload['page'] = page_num
                req = requests.get(url, params=payload).text
                company_pages.append(pd.read_html(req)[1][['시가', '고가', '저가', '현재가', '거래량', '종목명']])
                if page_num == 1: break
            if sosok == 0: break

        df = pd.concat(company_pages)
        current_prices = df
        current_prices.dropna(inplace=True)
        current_prices.reset_index(drop=True, inplace=True)
        current_prices.index = [datetime.today()] * len(current_prices)
        current_prices.columns = ['open', 'high', 'low', 'close', 'volume', 'codeName']
        return current_prices

    def load_data(self): ## 현재가만 구할 수 있으며 종가를 완벽하게 저장하기 위해서는 6시가 넘어야 한다.
        saved = pd.read_pickle('../Database/10year.pickle')
        result = saved
        if saved.index.unique().sort_values()[-1] < pd.to_datetime(datetime.today().strftime('%Y%m%d')):## 조건문을 안 넣으면 중첩된 날짜가 생길 우려
            print('업데이트 필요')
            current_prices = self.get_current_price()
            full_code = self.mg.full_code
            merged = current_prices.merge(full_code, on=['codeName'])
            adjust = merged[['open', 'high', 'low', 'close', 'volume', 'short_code']].copy()
            adjust.index = [pd.to_datetime(datetime.today().strftime('%Y%m%d'))] * len(adjust)
            result = pd.concat([saved, adjust])
            result.to_pickle('../Database/10year.pickle')

        else:
            print('업데이트 사항 없음')
        return result

if __name__ == "__main__":
    st = time.time()
    naver = naverreader()
    try:
        result = naver.get_naver_total(2500)
        print(result)
        # result.to_pickle('../Database/10year.pickle')
    except Exception as e:
        print(e)

    print('Wall time : {}분'.format((time.time() - st) / 60))