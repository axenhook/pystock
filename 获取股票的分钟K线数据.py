# 获取股票的分钟k线数据
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

# ====获取分总级别k线数据
# 返回指定股票的K线数据：https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz000001,day,,,50,qfq&r=0.5643184591626897
# 正常网址：https://gu.qq.com/sh000001/zs

# ====构建网址
# 参数
stock_code = 'sz000001'
k_type = 15  # 1、5、15、30、60分钟
num = 200 # 最多不能超过320

# 构建url
url = "http://ifzq.gtimg.cn/appstock/app/kline/mkline?param=%s,m%s,,%s&_var=m%s_today&r=0.%s"
url = url % (stock_code, k_type, num, k_type, _random())

# ====抓取数据
content = urlopen(url=url, timeout=15).read().decode()

# ====将数据转换成dict格式
content = content.split('=', maxsplit=1)[-1] # 去掉文本前面的多余字符
content = json.loads(content) 

# ====将数据转换成DataFrame格式
k_data = content['data'][stock_code]['m'+str(k_type)]
df = pd.DataFrame(k_data)

# ====对DataFrame进行整理
rename_dict = {0: 'candle_end_time', 1: 'open', 2: 'close', 3: 'high', 4: 'low', 5: 'amount'} # 自己去对比数据，会有新的发现
# 其中amount单位是手
df.rename(columns=rename_dict, inplace=True)
#df['candle_end_time'] = df['candle_end_time'].apply(lambda x: '%s-%s-%s %s:%s' % (x[0:4], x[4:6], x[6:8], x[8:10], x[10:12]))
df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount']]
print(df)

