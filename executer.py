from datamanager import datamanager
from strategy_ma import strategy_ma


stra = strategy_ma(30, 120, 60, 3000)
try:
    result = stra.run('20200212')
except Exception as e:
    print(e)

order = stra.get_order_for_exe(company_num=10, capital=200000000)
order.to_pickle('../Database/order{}.pickle'.format(stra.today))