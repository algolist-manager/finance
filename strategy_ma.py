import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from strategy import strategy
from datetime import datetime
import time


class strategy_ma(strategy):
    def __init__(self, period, long, short, param):
        super().__init__()
        self.period = period
        self.long = long
        self.short = short
        self.param = param


    def get_rel_data(self, short_code, date):  # 의사결정 판단 시점으로 기준으로 필요한 데이터들 얻기
        buffer = int(self.long / 10)  # 이동평균선은 단순히 날짜가 아니라 거래일자 수로 롤링된다. 따라서 날짜로만 보는 timedelta에 buffer가 필요.
        date = pd.to_datetime(date)
        rel_period = pd.bdate_range(end=date, periods=(self.long+self.period+buffer))
        start_dt = rel_period[0]
        com_df = self.price_data[self.price_data['short_code'] == short_code].copy()
        adj_close = com_df['close'].loc[start_dt:date].copy()
        data = adj_close
        return data

    def get_score(self, short_code, date, param):
        """
        필요한 데이터를 바탕으로 score를 얻기. param은 기울기의 점수 가중치
        :param short_code:
        :param date: 이평선을 보는 기준 시점
        :param param: 기울기의 점수 가중치
        :return: score : 점수를 준다.

        60, 120 이평선의 문제점 : 장단기 이동평균선이 매우 근접해 있는 경우에 기울기 값이 크게 나오는 경향이 있다.
        """

        data = self.get_rel_data(short_code, date)
        ma_long = data.rolling(self.long).mean()
        ma_short = data.rolling(self.short).mean()
        spread = ma_long - ma_short
        _period = self.period - 1
        spread_lately = spread.iloc[-_period:].copy()

        score = 0
        try:
            if min(spread_lately.values) > 0:
                divider = spread_lately[0]
                spread_ratio = spread_lately / divider
                x = np.array([range(len(spread_lately))]).T
                x = sm.add_constant(x)
                y = np.array([spread_ratio]).T
                slope = np.linalg.lstsq(x, y, rcond=None)[0][1][0]
                score = 100 - param * slope

        except ValueError:
            print('-----------------------{} 종목 데이터 에러'.format(short_code))

        except Exception as e:
            print(e)

        return score

    def decide_bool(self, short_code, date):  # score를 통해서 판단
        score = self.get_score(short_code, date, self.param)
        if score > 100:
            return True
        else:
            return False

    def run(self, date):
        """
        실제로 전략에 맞는 종목을 뽑아본다.
        ** 문제점
        이동평균선이 가파르게 치고 나가는 종목을 원했으나 실제로는 미세하게 치고 나가는 종목일수록 기울기 값이 크게 나옴.
        이동평균선이 이미 크로스된 종목의 경우에도 OLS 방법을 쓴 경우 기울기가 음수가 나온다.
        :param date:
        :return:
        """
        start = time.time()
        short_codes = list(self.naver_companies['short_code'].copy())
        codeNames = list(self.naver_companies['codeName'].copy())
        scores = []
        for idx, short_code in enumerate(short_codes):
            scores.append(self.get_score(short_code, date=date, param=self.param))
            if idx % 3 == 0:
                loading = (time.time() - start) / 60
                print('진행률 {0}%, 현재 소요시간 {1}분'.format(round(idx*100/len(short_codes), 2), round(loading, 2)))

        df_list = [short_codes, scores, codeNames]
        self.result = pd.DataFrame(df_list).T
        self.result.columns = ['short_code', 'score', 'codeName']
        self.result = self.result.sort_values('score', ascending=False).reset_index(drop=True)
        return self.result

    def get_order_for_bt(self, stocks, start, period=None, end=None):
        """
        Backtest에 order를 넣어줄 Simple portfolio(시작시점에 모든 종목을 같은 웨이트로 사서 보유)를 생성한다.
        :param stocks: (list) run에 나온 기업들 중 선정
        :param start:  (date.strftime %Y%m%d) 백테스트 시작 날짜
        :param period: (int) 보유 일수를 결정
        :param period: (date.strftime %Y%m%d) 최종 보유 시점을 결정

        :return: (DataFrame) order
        """
        bizdays = self.krxbizdays
        start = pd.to_datetime(start)
        if end is not None:
            end = pd.to_datetime(end)
            index = list(bizdays['krxbiz'].loc[start:end])
        else:
            index = list(bizdays['krxbiz'].loc[start:].iloc[:period + 1])

        init_port = [1] * len(stocks)
        order = pd.DataFrame(index=index, columns=stocks)
        order.iloc[0] = init_port
        order.fillna(0, inplace=True)
        return order

    def get_order_for_exe(self, company_num, capital, trade_day): ## company_num은 투자할 상위 종목 수, capital은 투자액
        trade_day = [pd.to_datetime(trade_day)]*company_num
        #pd.to_datetime(datetime.today().strftime('%Y%m%d'))
        short_codes = list(self.result['short_code'].iloc[:company_num])
        codenames = list(self.result['codeName'].iloc[:company_num])
        prices = self.price_data[self.price_data['short_code'].isin(short_codes)].loc[trade_day[0]][
            'close']  ## 12시 전에 돌리면 today고 아니면 today-timedelta(days=1)
        quantities = (capital / company_num) / prices
        quantities = quantities.apply(lambda x: int(x))
        order = pd.DataFrame([trade_day, short_codes, prices, quantities], columns=codenames,
                             index=['date', 'short_code', 'price', 'quantity'])
        order.loc['date'] = trade_day

        order = order.T
        order[['price', 'quantity']] = order[['price', 'quantity']].applymap(lambda x: int(x))
        return order




    def see_data_by_name(self, codeName):
        full_code = self.full_code.copy()
        price_data = self.price_data.copy()
        short_code = full_code[full_code['codeName'] == codeName]['short_code'].iloc[0]
        com_df = price_data[price_data['short_code'] == short_code].copy()
        com_df.sort_values(by=['date'], inplace=True)
        com_df['codeName'] = codeName
        plt.plot(com_df['adj'][-30:])
        plt.show()
        return com_df

    def see_data_by_code(self, short_code):
        full_code = self.full_code.copy()
        price_data = self.price_data.copy()
        codeName = full_code[full_code['short_code'] == short_code]['codeName'].iloc[0]
        com_df = price_data[price_data['short_code'] == short_code].copy()
        com_df.sort_values(by=['date'], inplace=True)
        com_df['codeName'] = codeName
        plt.plot(com_df['adj'][-30:])
        plt.show()
        return com_df

if __name__ == '__main__':
    stra = strategy_ma(30, 120, 60, 3000)
    print(stra.run('20200102').head(20))