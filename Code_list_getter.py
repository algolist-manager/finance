import requests
import pandas as pd
import json
import datetime


class Code_list_getter:
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://marketdata.krx.co.kr/mdi'
        }

        self.full_code_payload_otp = {
            'bld': 'COM/finder_stkisu',
            'name': 'form'
        }
        self.full_code_otp = requests.post('http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx',
                                           data=self.full_code_payload_otp,
                                           headers=self.header).text

        self.payload_full_code = {
            'no': 'P1',
            'mktsel': 'ALL',
            'pagePath': '/contents/COM/FinderStkIsu.jsp',
            'code': self.full_code_otp
        }

        self.payload_listed_otp = {
            'bld': 'MKD/04/0406/04060100/mkd04060100_01',
            'name': 'form'
        }
        self.listed_otp = requests.post('http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx',
                                        data=self.payload_listed_otp, headers=self.header).text
        self.listed_payload = {
            'market_gubun': 'ALL',
            'isu_cdnm': '전체',
            # isu_cd:
            # isu_nm:
            # isu_srt_cd:
            'sort_type': 'A',
            # std_ind_cd:
            # par_pr:
            # cpta_scl:
            # sttl_trm:
            'lst_stk_vl': 1,
            # in_lst_stk_vl:
            # in_lst_stk_vl2:
            'cpt': 1,
            # in_cpt:
            # in_cpt2:
            'isu_cdnm': '전체',
            # isu_cd:
            # mktpartc_no:
            # isu_srt_cd:
            'pagePath': '/contents/MKD/04/0406/04060100/MKD04060100.jsp',
            'code': self.listed_otp,
        }
        self.last_page = 236

    def get_full_code(self):
        p = []
        for i in range(1, 16):
            self.payload_full_code['consonant'] = i
            r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx',
                              data=self.payload_full_code,
                              headers=self.header).text
            p.append(pd.DataFrame(json.loads(r)['block1']))
        self.full_code = pd.concat(p)

    def get_code_list(self):
        res_list = []
        for i in range(1, self.last_page + 1):
            self.listed_payload['curPage'] = i
            try:
                res = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx',
                                    data=self.listed_payload, headers=self.header).text
            except Exception as e:
                print(e)
            res_list.append(json.loads(res)['block1'])
            print(i)

        df_list = []
        for x in res_list:
            df_list.append(pd.DataFrame(x))
        self.result = pd.concat(df_list)

    def preprocess(self):
        self.get_code_list()
        self.get_full_code()

        b = []
        for code in self.result['isu_cd']:
            a = 'A' + code
            b.append(a)
        self.result['short_code'] = b
        self.result['date'] = datetime.datetime.now()

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


if __name__ == '__main__':
    code_list_getter = Code_list_getter()
    code_list_getter.preprocess()
    code_list_getter.result.to_csv('./listed_company.csv', encoding='utf-8-sig', index=False)

## 마지막 페이지 정보를 가져오기
## 크롤러는 완전히 따로 분리하기 -> 시간이 오래 걸리기 때문에 모든 것이 한번에 날아갈 수 있음
