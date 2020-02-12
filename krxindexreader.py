import requests
import pandas as pd
import json
from krxreader import krxreader
"""
거래소에 상장된 지수 데이터를 가져오는 class
"""
class krxindexreader(krxreader):
    def __init__(self):
        super().__init__()
        self.otp_payload = {
            'bld': 'MKD/03/0304/03040101/mkd03040101T2_02',
            'name': 'form'
        }
        self.otp = requests.post(self.otp_url, data=self.otp_payload ,headers = self.header).text
        if len(self.otp) > 3:
            print('OTP : {}'.format(self.otp))
        else:
            print('OTP 확보 실패')
            raise ValueError
        self.index_code = {
            'KOSPI200' : '1028'
        }
        self.index_ind_code = {
            'KOSPI200' : '028'
        }

        self.search_history = []

    def get_index(self, fromdate, todate, indexname = None, ):
        idx_cd =  self.index_code[indexname]
        idx_ind_cd = self.index_ind_code[indexname]

        url ='http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx'

        payload = {
                'idx_cd': idx_cd, ## kospi200 = 1028
                'ind_tp_cd': '1',
                'idx_ind_cd': idx_ind_cd , ##kospi200 기본 = 028
                # 'add_data_yn':,
                'bz_dd': self.today,
                'indexname': '지수명을 입력해 주세요.',
                'chartType': 'line',
                'chartStandard': 'srate',
                'fromdate': fromdate,
                'todate': todate,
                'pagePath': '/contents/MKD/03/0304/03040101/MKD03040101T2.jsp',
                'code': self.otp
        }

        index_df = requests.post(url, data=payload, headers=self.header).text
        index_df = pd.DataFrame(json.loads(index_df)['output'])
        self.search_history.append(index_df)

        return index_df



