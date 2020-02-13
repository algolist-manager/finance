import pandas as pd
from datetime import datetime
from abc import *

class strategy():
    def __init__(self):
        self.today = datetime.today().strftime('%Y%m%d')
        self.full_code = pd.read_pickle('../Database/full_code.pickle')
        self.adj_total = pd.read_pickle('../Database/adj_total.pickle')
        self.price_data = pd.read_pickle('../Database/10year.pickle')
        self.krxbizdays = pd.read_pickle('../Database/krxbiz.pickle')
        self.naver_companies = pd.read_pickle('../Database/naver_companies.pickle')
        """
        이 부분은 DB 매니저가 만들어지면 그 양식으로 대체해야한다.
        """

        """
        아래의 3가지 함수를 포함하는 format으로 선정
        """
    @abstractmethod
    def get_rel_data(self, short_code, date): # 의사결정 판단 시점으로 기준으로 필요한 데이터들 얻기
        data = pd.DataFrame()
        return data

    @abstractmethod
    def get_score(self, short_code, date, param): # 필요한 데이터를 바탕으로 score를 얻기
        score = 100
        return score

    @abstractmethod
    def decide_bool(self, short_code, date): # score를 통해서 판단
        data = self.get_rel_data(short_code, date)
        score = self.get_score(data)
        if score > 100:
            return True
        else:
            return False









