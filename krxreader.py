from datetime import datetime
"""
krx 관련 데이터를 긁어오는 기본 토대
"""
class krxreader():
    def __init__(self):
        self.header = {
            'Referer': 'http://marketdata.krx.co.kr/mdi',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko Chrome/79.0.3945.130 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.otp_url = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx'
        self.today = datetime.today().strftime('%Y%m%d')

"""
data = krx.get_code_list() ## 현재 시점의 상장 데이터를 가져오는 함수
data = krx.get_stock_price('20100101', '20181231', mkt = 'TOTAL')
data = krx.get_stock_price('20100101', '20181231', mkt = 'KOSPI200')
data = krx.get_stock_price('20100101', '20181231', mkt = 'KOSPI')
data = krx.get_stock_price('20100101', '20181231', mkt = 'KOSDAQ')
data = krx.get_stock_price('20100101', '20181231', mkt = 'KONEX')

data = krx.get_stock_price('20100101', '20181231', codeName = 'KOSPI200')
data = krx.get_stock_price('20100101', '20181231', codeName = '삼성전자')
data = krx.get_stock_price('20100101', '20181231', codeName = ['삼성전자', 'SK하이닉스'])
"""