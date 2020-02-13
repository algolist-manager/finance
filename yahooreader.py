from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import phantomjs
import requests
import pandas as pd
import finance_util
import time
from bs4 import BeautifulSoup as bs


class yahooreader():
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        # self.driver = webdriver.PhantomJS('C:/phantomjs-2.1.1/bin/phantomjs.exe')
        self.driver = webdriver.Chrome('C:/chromedriver/chromedriver.exe', chrome_options=options)

    def get_adj_close(self, short_code, fromdate, todate):
        num_code = short_code[1:]
        dt1 = pd.to_datetime(fromdate)
        dt2 = pd.to_datetime(todate)
        days = len(pd.date_range(dt1, dt2, freq="B"))

        fromdate = finance_util.to_unix(fromdate)
        todate = finance_util.to_unix(todate)
        url = 'https://finance.yahoo.com/quote/{0}.KS/history?period1={1}&period2={2}&interval=1d&filter=history&frequency=1d' \
            .format(num_code, fromdate, todate)
        self.driver.get(url)
        time.sleep(3)

        """
        time_period_button = self.driver.find_element_by_css_selector(
            '#Col1-1-HistoricalDataTable-Proxy > section > div.Mt\(15px\).drop-down-selector.historical > div.Bgc\(\$lv1BgColor\).Bdrs\(3px\).P\(10px\) > div:nth-child(1) > div > div > div > svg')
        time_period_button.click()
        max_button = self.driver.find_element_by_css_selector(
            '#dropdown-menu > div > ul:nth-child(2) > li:nth-child(4) > button')
        max_button.click()
        soup = bs(self.driver.page_source, 'lxml')
        max_date = pd.to_datetime(soup.find('span', class_='C($linkColor) Fz(14px)').text.split('-')[0].strip())
        """

        element = self.driver.find_element_by_css_selector('#yfin-usr-qry')
        scr_no = int(days/6)
        cnt=0
        print('스크롤 시작')
        while True:
            for _ in range(scr_no):
                element.send_keys(Keys.PAGE_DOWN)

            adj_price = pd.read_html(self.driver.page_source)[0].iloc[:-1]
            if (len(adj_price) < (days*0.9)):
                print('{}종목 크롤링 개수 부족'.format(short_code))
                cnt +=1
                if cnt == 2:
                    break

            else:
                break



        return adj_price










