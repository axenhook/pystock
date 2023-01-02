# 获取股票的日k线数据
from urllib.request import urlopen # python自带爬虫库
import json  # python自带的json数据库
from random import randint  # python自带的随机数库
import pandas as pd
pd.set_option('expand_frame_repr', False) # 当列太多时不换行
pd.set_option('display.max_rows', 5000)   # 最多显示数据的行数

# ====创建随机数的函数
def _random(n=16):
    """
    创建一个n位的随机整数
    ;param n:
    ;return:
    """
    start = 10**(n - 1)
    end = (10**n) - 1
    return str(randint(start, end))

# ====获取日、周、月的k线数据
# 返回指定股票的K线数据：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz000001,day,,,50,qfq&r=0.5643184591626897
# 正常网址：https://gu.qq.com/sh000001/zs

# ====构建网址
# 参数
stock_code = 'sh600276'
k_type = 'day'  # day, week, month分别对应日线、周线、月线
num = 10 # 股票最多不能640，指数、etf等没有限制

# 构建url
url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_%sqfq&param=%s,%s,,,%s,qfq&r=0.%s"
url = url % (k_type, stock_code, k_type, num, _random())

# ====抓取数据
content = urlopen(url).read().decode()

# ====将数据转换成dict格式
content = content.split('=', maxsplit=1)[-1] # 去掉文本前面的多余字符
content = json.loads(content) 

# ====将数据转换成DataFrame格式
k_data = content['data'][stock_code]
if k_type in k_data
    k_data = k_data[k_type]
elif 'qfq' + k_type in k_data: # qfq是前复权的缩写
    k_data = k_data['qfq' + k_type]
else:
    raise ValueError('已知的key在dict中均不存在，请检查数据')
df = pd.DataFrame(k_data)

# ====对DataFrame进行整理
rename_dict = {0: 'candle_end_time', 1: 'open', 2: 'close', 3: 'high', 4: 'low', 5: 'amount', 6: 'info'} # 自己去对比数据，会有新的发现
# 其中amount单位是手
df.rename(columns=rename_dict, inplace=True)
df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
if 'info' not in df:
    df['info'] = None
df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount', 'info']]

# ====考察退市、停牌股票
# 根据特征删除股票数据
df = df[df['open'] - 0 > 0.00001]

# ====考察新上市的股票
# 对于新上市的股票，pre_close指的是发行价

# ====考察除权股票
# 对于今天除权的股票，pre_close不是昨天真正的收盘价，而是交易所计算出来且公布的昨天的收盘价
# 有了这个数据，才能算出这个股票真正的涨跌幅


