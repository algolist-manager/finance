import statsmodels.formula.api as smf
import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def decider(short_code):
    checker = True
    slope = 0
    full_code = pd.read_pickle('./full_code.pickle')
    new_all_total = pd.read_pickle('./new_all_total.pickle')
    codeName = full_code[full_code['short_code'] == short_code].iloc[0, -2]
    data_num = 30
    com_df = new_all_total[new_all_total['short_code'] == short_code]
    com_df.sort_values(by=['date'], inplace=True)
    ma_120 = com_df['adj'].rolling(120).mean()
    ma_60 = com_df['adj'].rolling(60).mean()
    spread = ma_120 - ma_60
    com_df['spread'] = spread
    com_df_lately = com_df.iloc[-(data_num - 1):]

    if max(com_df_lately['spread']) >= 0:
        print('부적절')
        checker = False
    else:
        divider = com_df_lately.iloc[0, -1]
        com_df_lately['spread_ratio'] = com_df_lately['spread'] / divider
        com_df_lately = com_df_lately.reset_index().reset_index()

        x = np.array([com_df_lately.index]).T
        x = sm.add_constant(x)
        y = np.array([com_df_lately['spread_ratio']]).T
        slope = np.linalg.lstsq(x, y)[0][1][0]

        print('{0}의 1개월 이동평균 spread 기울기 : {1}'.format(codeName, slope))
        plt.plot(com_df_lately.index, com_df_lately['spread_ratio'])
        plt.show()

    return checker, short_code, codeName, slope


all_total = pd.read_pickle('./all_total.pickle')
short_code_list = all_total['short_code'].unique()
decide_list = []
for idx, short_code in enumerate(short_code_list):
    remain = len(short_code_list) - idx
    checker, short_code, codeName, slope = decider(short_code)
    print('남은 개수 : {0} {1}'.format(remain, codeName))
    decide_list.append((checker, short_code, codeName, slope))
