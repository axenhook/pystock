# 结合预测者网的历史数据，每天获取股票的数据，构建完整实时股票数据库

from urllib.request import urlopen  # python自带爬虫库
import json  # python自带的json数据库
from datetime import datetime
import time
import re  # 正则表达式库
import os
import pandas as pd
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)   # 最多显示数据的行数


def get_content_from_internet(url, max_try_num=10, sleep_time=5):
    """
    使用python自带的urlopen函数，从网页上抓取数据
    :param url: 要抓取数据的网址
    :param max_try_num: 最多尝试抓取的次数
    :param sleep_time: 抓取失败后停顿的时间
    :return: 返回抓取到的网页内容
    """
    get_success = False  # 是否成功抓取到内容
    # 抓取内容
    for i in range(max_try_num):
        try:
            content = urlopen(url=url, timeout=10).read()  # 从网络上抓取数据
            get_success = True
            break
        except Exception as e:
            print('抓取数据出错，次数: ', i + 1, '报错内容：', e)
            time.sleep(sleep_time)

    # 判断是否成功抓取内容
    if get_success:
        return content
    else:
        raise ValueError('使用urlopen抓取网页数据不断报错，请尽快检查问题所在')


def get_today_data_from_sinajs(code_list):
    """
    返回指定股票最近一个交易日的相关数据：从新浪获取指定股票的数据
    数据获取网址：http://hq.sinajs.cn/list=sh600000,sz000002,sz300001
    正常网址：https://finance.sina.com.cn/realstock/company/sh600000/nc.shtml
    :para code_list: 股票代码list，可以多个
    :return:返回一个存储股票数据的DataFrame
    """

    # ====构建网址
    url = "http://hq.sinajs.cn/rn=1672628899212&list=" + ",".join(code_list)
    # print(url)
    # exit(0)

    # ====抓取数据
    content = get_content_from_internet(url)
    content = content.decode('gbk')
    print(content)

    # ====将数据转换成DataFrame
    content = content.strip()  # 去掉文本前后的空格、回车等
    data_line = content.split('\n')  # 每行是一个股票的数据
    data_line = [i.replace('var hq_str_', '').split(',') for i in data_line]
    df = pd.DataFrame(data_line, dtype='float')

    # ====对DataFrame进行整理
    df[0] = df[0].str.split('="')
    df['stock_code'] = df[0].str[0].strip()
    df['stock_name'] = df[0].str[-1].strip()
    df['candle_end_time'] = df[30] + ' ' + df[31]  # 股票市场的k线，是普遍以当前K线结束时间来命名的
    rename_dict = {1: 'open', 2: 'pre_closed', 3: 'closed', 4: 'high', 5: 'low', 6: 'buy1', 7: 'sell1',
                   8: 'amount', 9: 'volume', 32: 'status'}  # 自己去对比数据，会有新的发现
    # 其中amount单位是股，volume单位是元
    df.rename(columns=rename_dict, inplace=True)
    df['status'] = df['status'].str.strip('";')
    df = df[['stock_code', 'stock_name', 'candle_end_time', 'open', 'high', 'low', 'closed',
            'pre_closed', 'buy1', 'sell1', 'status']]

    # ====考察退市、停牌股票
    # 根据特征删除股票数据
    df = df[df['open'] - 0 > 0.00001]

    return df


def is_today_trading_day():
    """
    判断今天是否是交易日
    :return: 如果是返回True，否则返回False
    """
    # 获取上证指数今天的数据
    df = get_today_data_from_sinajs(code_list=['sh000001'])
    sh_date = df.iloc[0]['candle_end_time']  # 上证指数最近交易日

    # 判断今天日期和sh_date是否相同
    return sh_date.date() == datetime.now().date()


def get_all_today_stock_data_from_sina_marketcenter():
    """从新浪获取所有股票的数据
    从https://vip.stock.finance.sina.com.cn/mkt/#stock_hs_up，逐页获取最近一个交易日所有股票的数据
    :return: 返回一个存储股票数据的DataFrame
    """
    # 数据网址
    raw_url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=%s&num=40&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=auto'
    page_num = 1

    # 存储数据的DataFrame
    all_df = pd.DataFrame()

    # 逐页遍历，获取股票数据
    while True:
        # 构建url
        url = raw_url % (page_num)
        print('开始抓取page: ', page_num)

        # 抓取数据
        content = get_content_from_internet(url)
        content = content.decode('gbk')

        # 通过正则表达式，给key加上引号
        # content = re.sub(r'(?<={|,)([a-zA-Z][a-zA-Z0-9]*)(?=:)', r'"\1"', content)
        # print(content)

        # 将数据转换成dict格式
        content = json.loads(content)

        # content是一个list，判断list是否为空
        if len(content) == 0:
            print('所有网页都已抓完，退出循环')
            break

        # 将数据转换成DataFrame格式
        df = pd.DataFrame(content)

        # 对数据进行整理
        # 重命名
        rename_dict = {'symbol': '股票代码', 'name': '股票名称', 'open': '开盘价',
                       'high': '最高价', 'low': '最低价', 'trade': '收盘价', 'settlement': '前收盘价', 'volume': '成交量',
                       'amount': '成交额', 'nmc': '流通市值', 'mktcap': '总市值'}
        df.rename(columns=rename_dict, inplace=True)
        # 添加交易日期
        df['交易日期'] = pd.to_datetime(datetime.now().date())
        # 取需要的列
        df = df[['股票代码', '股票名称', '交易日期', '开盘价', '最高价', '最低价',
                 '收盘价', '前收盘价', '成交量', '成交额', '流通市值', '总市值']]
        df['流通市值'] = df['流通市值'].map(lambda x: x*10000)
        df['总市值'] = df['总市值'].map(lambda x: x*10000)

        # 合并数据
        all_df = all_df.append(df, ignore_index=True)

        # 页数+1
        page_num += 1
        time.sleep(1)
        # break

    return all_df


def main():
    """
    if is_today_trading_day() is False:
        print('今天不是交易日，不需要更新股票数据，退出程序')
        exit()
    """

    if datetime.now().hour < 15:  # 保险起见可以小于16点
        print('今天股票尚未收盘，暂不更新股票数据，退出程序')
        exit()

    # 更新数据思路
    # 通过get_all_today_stock_data_from_sina_marketcenter获取所有股票数据
    df = get_all_today_stock_data_from_sina_marketcenter()

    # 存储数据
    for i in df.index:
        t = df.iloc[i:i+1, :]
        stock_code = t.iloc[0]['股票代码']

        # 构建存储文件路径
        path = "..\\stock_data\\" + stock_code + ".csv"
        # 文件存在,不是新股
        if os.path.exists(path):
            t.to_csv(path, header=None, index=False, mode='a', encoding='gbk')
        # 文件不存在,是新股
        else:
            pd.DataFrame(columns=['数据由axen整理']).to_csv(
                path, index=False, encoding='gbk')
            t.to_csv(path, index=False, mode='a', encoding='gbk')


if __name__ == '__main__':
    main()
