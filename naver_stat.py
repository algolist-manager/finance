import requests
import pandas as pd
url = 'https://finance.naver.com/item/main.nhn?'
payload = {
    'code' : '035720'
}
r = requests.get(url, params=payload).text
x = pd.read_html(r)
print(len(x))
print(x[3])