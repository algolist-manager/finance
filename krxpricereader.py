import requests
import json
import pandas as pd
from datetime import datetime
from matplotlib.pyplot import plot, show
import finance_util
from krxreader import krxreader
"""
특정 종목의 주가 데이터를 가져오는 클래스
"""
class krxpricereader(krxreader):
    def __init__(self):
        super().__init__()
        self.otp_payload = {
            'bld': 'MKD/04/0402/04020100/mkd04020100t3_02',
            'name': 'form'
        }
        self.otp = requests.post('http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx', data=self.otp_payload,
                                 headers=self.header).text


        self.code_list = pd.read_pickle('../Database/full_code.pickle')

    def get_stock_price_all(self, fromdate, todate):
        for idx, short_code in enumerate(self.code_list['short_code']):
            full_code, num_code, codeName = self.get_stock_price(short_code, fromdate, todate)
            print(idx, '{0} {1} {2} 데이터 수집중....'.format(full_code, num_code, codeName))


    def get_stock_price(self, short_code, fromdate, todate):  ## 여기서 short_code는 A005930 형식
        payload = {
            'pagePath': '/contents/MKD/04/0402/04020100/MKD04020100T3T2.jsp',
            'code': self.otp
        }

        codeName = self.code_list[self.code_list['short_code'] == short_code].iloc[0]['codeName']
        full_code = self.code_list[self.code_list['short_code'] == short_code].iloc[0]['full_code']

        payload['isu_cdnm'] = short_code + '/' + codeName
        payload['isu_cd'] = full_code
        payload['isu_nm'] = codeName
        payload['isu_srt_cd'] = short_code
        payload['fromdate'] = fromdate  ## 왜 여기에 self를 쓸 수 없을까.
        payload['todate'] = todate  ## 왜 여기에 self를 쓸 수 없을까.

        try:
            res = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload,
                                headers=self.header)
            raw = pd.DataFrame(json.loads(res.text)['block1'])
            raw['trd_dd'] = pd.to_datetime(raw['trd_dd'])
            raw['tdd_clsprc'] = raw['tdd_clsprc'].apply(lambda x: int(x.replace(',', '')))
            raw['short_code'] = short_code
            raw['codeName'] = codeName
            raw.set_index('trd_dd', drop=True, inplace=True)
            raw.sort_index()

            if len(raw) < 5:
                print('길이가 5보다 작음')
        except Exception as e:
            print(e)
            print(
                '에러가 발생했습니다-----------------------------------------------------------------------------------')

        return raw
        # 좀 더 개량한다면 index에 date가 들어가도록 할 수 있다. 그럴 때 인덱스를 추출하는 방법?



    def preprocess(self):
        col = ['short_code', 'codeName', 'trd_dd', 'tdd_clsprc', 'fluc_tp', 'tdd_cmpr', 'tdd_hgprc', 'tdd_lwprc' ,
               'tdd_opnprc', 'acc_trdval', 'acc_trdvol', 'list_shrs', 'mktcap']
        col_1 = ['short_code', 'codeName', 'date', 'close_price', 'up_down', 'diff', 'high_price', 'low_price',
                 'open_price', 'trd_vol_won', 'trd_vol_stocks', 'listed_shares', 'market_cap']
        col_re = dict()
        for i in range(len(col)):
            bf = col[i]
            af = col_1[i]
            col_re[bf] = af
        raw1 = self.result[col]
        raw1.rename(columns=col_re, inplace=True)

        raw1['date'] = raw1['date'].apply(lambda x: finance_util.to_date(x))
        int64_dat = ['close_price', 'diff', 'high_price', 'low_price', 'open_price', 'trd_vol_won', 'trd_vol_stocks',
                     'listed_shares','market_cap']
        raw1[int64_dat] = raw1[int64_dat].applymap(lambda x: int(x.replace(',', '')))
        self.fined_result = raw1
        return self.fined_result


    def update(self):
        pass

    def plotting(self, small_stock_price):
        plot(small_stock_price['trd_dd'], small_stock_price['adj'])
        show()



#### 주간에는 주가 정보 데이터를 크롤링 불가. 연결이 안된다고 나온다.
#### 이름으로 찾기, 코드로 찾기, A붙은 코드로 찾기 등으로 다양화 할 수 있다.
#### raw 데이터 내에 들어있는 정보도 중요한 것이 많기 때문에 이 정보도 저장해두고 싶다.
#### 이 클래스 내의 self.total이라는 데이터가 날짜 기간이라는 label을 가지게 하고 싶다.
#### 대안 : init에 self.fromdate, self.todate를 정한다.
#### 업데이트 문제의 해결 / 이미 있는 데이터인지 빠르게 확인, Windows에 작업 자동화 등록, 데이터 프레임 열 추가, sort
#### 데이터 수집 클래스를 아예 나누기
#### csv로 저장할 때 type이 바뀐다 -> DB로 저장하기


