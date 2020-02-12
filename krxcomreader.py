import requests
import pandas as pd
import json
from krxreader import krxreader

"""
상장 종목 전체의 업종, 자본금, 상장주식수에 대한 현황을 가져오는 class / 개별회사는 없음
"""
class krxcomreader(krxreader):
    def __init__(self):
        super().__init__()
        self.otp_payload = {
            'bld': 'MKD/04/0406/04060100/mkd04060100_01',
            'name': 'form'
        }
        self.otp = requests.post(self.otp_url, data=self.otp_payload ,headers = self.header).text
        if len(self.otp) > 3:
            print('OTP : {}'.format(self.otp))
        else:
            print('OTP 확보 실패')
            raise ValueError

    def get_company_info(self):
        payload = {
            'market_gubun': 'ALL',
            'isu_cdnm': '전체',
            'sort_type': 'A',
            'lst_stk_vl': 1,
            'cpt': 1,
            'pagePath': '/contents/MKD/04/0406/04060100/MKD04060100.jsp',
            'code': self.otp,
        }
        last_page = 236

        page_list = []
        for i in range(1, last_page + 1):
            payload['curPage'] = i
            try:
                r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx',
                                    data=payload, headers=self.header).text
                page_list.append(json.loads(r)['block1'])
            except Exception as e:
                print(e)

        companies_list = []
        for page in page_list:
            companies_list.append(pd.DataFrame(page))
        self.company_info = pd.concat(companies_list)

        return self.company_info