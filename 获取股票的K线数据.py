# 从网站获取股票数据的基础函数

from urllib.request import urlopen  # python自带爬虫库
import json  # python自带的json数据库
from random import randint  # python自带的随机数库
import pandas as pd
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)   # 最多显示数据的行数


def _random(n=16):
    """获取一个n位的随机整数
    :param n: 随机数的位数
    :returns: 获取到的随机数
    """
    start = 10**(n - 1)
    end = (10**n) - 1
    return str(randint(start, end))


def get_stock_days(stock_code, k_type, num):
    """ 获取股票的日、周、月的k线数据，获取股票数据的网址：https://gu.qq.com/sh000001/zs
    :param stock_code: 股票代码，也可以是指数、ETF等
    :param k_type: k线类型，day、week、month分别对应日线、周线、月线，可考察其他周期
    :param num: k线的数量，股票最多不能超过640，指数、etf等没有限制
    :returns: 包含股票数据的DataFrame
    """

    # 构建url
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_%sqfq&param=%s,%s,,,%s,qfq&r=0.%s"
    url = url % (k_type, stock_code, k_type, num, _random())

    # ====抓取数据
    content = urlopen(url).read().decode()

    # ====将数据转换成dict格式
    content = content.split('=', maxsplit=1)[-1]  # 去掉文本前面的多余字符
    content = json.loads(content)

    # ====将数据转换成DataFrame格式
    k_data = content['data'][stock_code]
    if k_type in k_data:
        k_data = k_data[k_type]
    elif 'qfq' + k_type in k_data:  # qfq是前复权的缩写
        k_data = k_data['qfq' + k_type]
    else:
        raise ValueError('已知的key在dict中均不存在，请检查数据')
    df = pd.DataFrame(k_data)

    # ====对DataFrame进行整理
    rename_dict = {0: 'candle_end_time', 1: 'open', 2: 'close',
                   3: 'high', 4: 'low', 5: 'amount', 6: 'info'}  # 自己去对比数据，会有新的发现
    # 其中amount单位是手
    df.rename(columns=rename_dict, inplace=True)
    df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
    if 'info' not in df:
        df['info'] = None
    df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount', 'info']]
    print(df)



def get_stock_minutes(stock_code, k_type, num):
    """ 获取股票分钟级别k线的数据，获取股票数据的网址：https://gu.qq.com/sh000001/zs
    :param stock_code: stock code
    :param k_type: 分钟k线的类型，如1、5、15、30、60分钟
    :param num: k线的数量，最多不能超过320
    :returns: 包含股票数据的DataFrame
    """

    # 构建url
    url = "http://ifzq.gtimg.cn/appstock/app/kline/mkline?param=%s,m%s,,%s&_var=m%s_today&r=0.%s"
    url = url % (stock_code, k_type, num, k_type, _random())

    # ====抓取数据
    content = urlopen(url=url, timeout=15).read().decode()

    # ====将数据转换成dict格式
    content = content.split('=', maxsplit=1)[-1]  # 去掉文本前面的多余字符
    content = json.loads(content)

    # ====将数据转换成DataFrame格式
    k_data = content['data'][stock_code]['m'+str(k_type)]
    df = pd.DataFrame(k_data)

    # ====对DataFrame进行整理
    rename_dict = {0: 'candle_end_time', 1: 'open', 2: 'close',
                   3: 'high', 4: 'low', 5: 'amount'}  # 自己去对比数据，会有新的发现
    # 其中amount单位是手
    df.rename(columns=rename_dict, inplace=True)
    # df['candle_end_time'] = df['candle_end_time'].apply(lambda x: '%s-%s-%s %s:%s' % (x[0:4], x[4:6], x[6:8], x[8:10], x[10:12]))
    df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])
    df = df[['candle_end_time', 'open', 'high', 'low', 'close', 'amount']]

    return df


def main():
    df = get_stock_minutes('sz000001', 15, 200)
    print(df)

    df = get_stock_days('sz000001', 'day', 100)
    print(df)


if __name__ == '__main__':
    main()
