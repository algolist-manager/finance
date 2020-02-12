from backtester import backtester
import pandas as pd
order = pd.read_pickle('../Database/order_sample.pickle')
order.fillna(0,inplace=True)

order.head()

bt = backtester(order)

bt.run()

