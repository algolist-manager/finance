import pandas as pd
import win32com.client
from datetime import datetime


class buyer():
    def __init__(self, order=None):
        self.connection()
        self.companies = pd.read_pickle('../Database/naver_companies.pickle')
        if order is not None:
            self.order = order

    def connection(self):
        obj = win32com.client.Dispatch('CpUtil.CpCybos')
        if obj.Isconnect == 1:
            print('Cybos가 정상적으로 연결되었습니다')
        else:
            print('연결 안 됨')

    def trd_stock_setting(self, short_code, order_quantity, order_price):
        tradeobj = win32com.client.Dispatch('CpTrade.CpTdUtil')
        print(tradeobj.TradeInit(0))  # 주문 초기화 /
        acc = tradeobj.AccountNumber[0]  # 계좌 번호
        goods_type = tradeobj.GoodsList(acc, 1)[0]  # 1은 주식, 2는 선물/옵션

        stockorder = win32com.client.Dispatch('CpTrade.CpTd0311')
        if order_quantity > 0:  # 매도 1, 매수 2
            buysell = '2'
        else:
            buysell = '1'
        acc_num = acc  # 계좌번호
        goods_type = '10'  # 주식 상품 구분
        short_code = short_code  # SK 하이닉스 종목코드
        quantity = abs(order_quantity)  # 수량
        price = order_price  # 호가
        order_type = '0'  # 0은 기본값, IOC는 1, FOK는 2
        call_type = '01'  # 지정가 01, 임의 02, 시장가 03, 조건부지정가 05, 최유리 12, 최우선 13

        stockorder.SetInputValue(0, buysell)
        stockorder.SetInputValue(1, acc_num)
        stockorder.SetInputValue(2, goods_type)
        stockorder.SetInputValue(3, short_code)
        stockorder.SetInputValue(4, quantity)
        stockorder.SetInputValue(5, price)
        # stockorder.SetInputValue(6,)
        stockorder.SetInputValue(7, order_type)
        stockorder.SetInputValue(8, call_type)

        return stockorder

    def request(self, obj):
        obj.BlockRequest()
        st_msg = obj.GetDibMsg1()
        print(st_msg)

    def trade(self):
        """
        세팅을 다 해두고 request를 하면 여러 종목을 매수할 수 있는지 확인해봐야 함. 일단은 한 종목씩 매수
        :param order:
        :return:
        """
        for codeName in self.order.index:
            short_code = self.order['short_code'].loc[codeName]
            quantity = self.order['quantity'].loc[codeName]
            price = self.order['price'].loc[codeName]
            if quantity > 0:
                buysell = '매수'
            else:
                buysell = '매도'
            print('{} 종목 {}주 {}원에 {}'.format(codeName, quantity, price, buysell))
            stockorder = self.trd_stock_setting(short_code, quantity, price)
            self.request(stockorder)

    def check_contract(self):
        account = win32com.client.Dispatch('CpTrade.CpTd5341')

        sort_type = '0'  # 순차 0, 역순 1
        num_data = 20  # default 7, maximum 20
        inq_type = '1'  # 단가별 : 1, 건별 : 2, 합산 : 3

        tradeobj = win32com.client.Dispatch('CpTrade.CpTdUtil')
        acc = tradeobj.AccountNumber[0]  # 계좌 번호
        goods_type = '10'
        num_data = 20
        inq_type = '1'

        account.SetInputValue(0, acc)  # 계좌번호
        account.SetInputValue(1, goods_type)  # 상품관리구분코드
        # account.SetInputValue(2,) # 종목코드 / 생략 시 전 종목
        # account.SetInputValue(3,) # 시작주문번호 / 생략 시 전 종목
        account.SetInputValue(4, sort_type)  # 정렬 / 0은 순차, 1은 역순
        account.SetInputValue(5, num_data)  # 요청개수 / 기본 7개 최대 20개
        account.SetInputValue(6, inq_type)  # 조회구분 / 1 단가별 2 건별, 3 합산

        account.BlockRequest()

        orders_list = []
        col = ['상품구분', '주문번호', '원주문번호', '종목코드', '종목이름', '주문내용',
               '주문수량', '주문단가', '총체결수량', '체결수량', '체결단가', '확인수량']
        for i in range(len(self.order)):
            order_list = []
            for j in range(13):
                if j == 6:
                    continue
                order_list.append(account.GetDataValue(j, i))
            orders_list.append(order_list)

        account_df = pd.DataFrame(orders_list, columns=col)
        return account_df
