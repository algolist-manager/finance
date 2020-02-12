import requests
import pandas as pd
import json
from datetime import datetime
from krxreader import krxreader
"""
거래소에 상장된 모든 종목의 코드를 가져오는 class
"""
class krxcodereader(krxreader):
    def __init__(self):
        super().__init__()
        self.otp_payload = {
            'bld': 'COM/finder_stkisu',
            'name': 'form'
        }
        self.otp = requests.post('http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx',
                                           data=self.full_code_payload_otp,
                                           headers=self.header).text
        if len(self.otp) > 3:
            print('OTP : {}'.format(self.otp))
        else:
            print('OTP 확보 실패')
            raise ValueError

    def get_full_code(self):
        payload = {
            'no': 'P1',
            'mktsel': 'ALL',
            'pagePath': '/contents/COM/FinderStkIsu.jsp',
            'code': self.otp
        }
        p = []
        for i in range(1, 16):
            self.payload_full_code['consonant'] = i
            r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx',
                              data=payload,
                              headers=self.header).text
            p.append(pd.DataFrame(json.loads(r)['block1']))

        self.full_code = pd.concat(p)
        return self.full_code

    def preprocess(self):
        self.get_code_list()
        self.get_full_code()

        b = []
        for code in self.result['isu_cd']:
            a = 'A' + code
            b.append(a)
        self.result['short_code'] = b
        self.result['date'] = datetime.now()

        del self.result['iso_cd']
        del self.result['tel_no']
        del self.result['addr']
        del self.result['totCnt']
        del self.result['no']

        self.result['full_code'] = 0
        self.result['marketName'] = 0
        ful = []
        mkt = []
        for x in self.result.iloc[:, -4]:
            y = self.full_code[self.full_code['short_code'] == x]
            ful.append(y['full_code'].values[0])
            mkt.append(y['marketName'].values[0])

        self.result['full_code'] = ful
        self.result['marketName'] = mkt

        self.result = self.result[
            ['date', 'full_code', 'short_code', 'isu_cd', 'kor_cor_nm', 'std_ind_cd', 'std_ind_nm', 'lst_stk_vl',
             'cpt',
             'par_pr', 'marketName']]

        self.result.rename(columns={
            'isu_cd': 'num_code', 'kor_cor_nm': 'codeName', 'std_ind_cd': 'std_ind_code',
            'std_ind_nm': 'std_ind_name', 'lst_stk_vl': 'isu_vol', 'cpt': 'common_stock',
            'par_pr': 'par_price'
        }, inplace=True)

        self.result[['isu_vol', 'common_stock']] = self.result[['isu_vol', 'common_stock']].applymap(
            lambda x: int(x.replace(',', '')))
        self.result['par_price'] = self.result['par_price'].apply(lambda x: float(x.replace(',', '')))

    def update(self):
        pass




## 마지막 페이지 정보를 가져오기
## 크롤러는 완전히 따로 분리하기 -> 시간이 오래 걸리기 때문에 모든 것이 한번에 날아갈 수 있음
