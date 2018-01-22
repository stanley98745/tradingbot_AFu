
import requests
from bs4 import BeautifulSoup
import re
import json
import pandas


res = requests.get('https://www.coingecko.com/zh-tw/%E5%8C%AF%E7%8E%87%E5%9C%96/zcash/usd')
soup = BeautifulSoup(res.text, 'html.parser')

data_prices = soup.select('#coin_portfolio_price_chart_zec')[0].prettify('utf-8').decode('utf-8')


m = re.search('<div class="coin_portfolio_price_chart" data-prices="(.*?)"', data_prices)

jd = json.loads(m.group(1))

df = pandas.DataFrame(jd)

df.columns = ['datetime', 'usd']

df['datetime'] = pandas.to_datetime(df['datetime'], unit='ms')

df.head()

df.index = df['datetime']

get_ipython().magic('pylab inline')
df['usd'].plot(kind = 'line', figsize = [10,5])

df['moveaverage7'] = df['usd'].rolling(window = 7).mean()

df[['usd','moveaverage7']].plot(kind = 'line', figsize = [20,5])




