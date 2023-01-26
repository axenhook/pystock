# 从baostock.com下载历史数据
import baostock as bs
import pandas as pd
import os

#### 获取沪深A股历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
# 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
# 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
# 返回数据说明
# 参数名称	参数描述	算法说明
# date	交易所行情日期
# code	证券代码
# open	开盘价
# high	最高价
# low	最低价
# close	收盘价
# preclose	前收盘价	见表格下方详细说明
# volume	成交量（累计 单位：股）
# amount	成交额（单位：人民币元）
# adjustflag	复权状态(1：后复权， 2：前复权，3：不复权）
# turn	换手率	[指定交易日的成交量(股)/指定交易日的股票的流通股总股数(股)]*100%
# tradestatus	交易状态(1：正常交易 0：停牌）
# pctChg	涨跌幅（百分比）	日涨跌幅=[(指定交易日的收盘价-指定交易日前收盘价)/指定交易日前收盘价]*100%
# peTTM	滚动市盈率	(指定交易日的股票收盘价/指定交易日的每股盈余TTM)=(指定交易日的股票收盘价*截至当日公司总股本)/归属母公司股东净利润TTM
# pbMRQ	市净率	(指定交易日的股票收盘价/指定交易日的每股净资产)=总市值/(最近披露的归属母公司股东的权益-其他权益工具)
# psTTM	滚动市销率	(指定交易日的股票收盘价/指定交易日的每股销售额)=(指定交易日的股票收盘价*截至当日公司总股本)/营业总收入TTM
# pcfNcfTTM	滚动市现率	(指定交易日的股票收盘价/指定交易日的每股现金流TTM)=(指定交易日的股票收盘价*截至当日公司总股本)/现金以及现金等价物净增加额TTM
# isST	是否ST股，1是，0否
def get_day_line(code, start, end):
    # 通过API接口获取A股历史交易数据，可以通过参数设置获取日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据，适合搭配均线数据进行选股和分析。
    # 能获取1990-12-19至当前时间的数据；
    # 可查询不复权、前复权、后复权数据。
    # 参数含义：
    # code：股票代码，sh或sz.+6位数字代码，或者指数代码，如：sh.601398。sh：上海；sz：深圳。此参数不可为空；
    # fields：指示简称，支持多指标输入，以半角逗号分隔，填写内容作为返回类型的列。详细指标列表见历史行情指标参数章节，日线与分钟线参数不同。此参数不可为空；
    # start：开始日期（包含），格式“YYYY-MM-DD”，为空时取2015-01-01；
    # end：结束日期（包含），格式“YYYY-MM-DD”，为空时取最近一个交易日；
    # frequency：数据类型，默认为d，日k线；d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据，不区分大小写；指数没有分钟线数据；周线每周最后一个交易日才可以获取，月线每月最后一个交易日才可以获取。
    # adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权。 BaoStock提供的是涨跌幅复权算法复权因子，具体介绍见：复权因子简介或者BaoStock复权因子简介。
    rs = bs.query_history_k_data_plus(code,
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        start_date=start, end_date=end,
        frequency="d", adjustflag="3")
    if rs.error_code != '0':
        print('query_history_k_data_plus respond error_code:%s, error_msg: %s' % (rs.error_code, rs.error_msg))
        #exit(rs.error_code)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    return result

def get_minute_line(code, start, end, freq):
    rs = bs.query_history_k_data_plus(code,
        "date,time,code,open,high,low,close,volume,amount,adjustflag",
        start_date=start, end_date=end,
        frequency=freq, adjustflag="3")
    if rs.error_code != '0':
        print('query_history_k_data_plus respond error_code:%d, error_msg: %s' % (rs.error_code, rs.error_msg))
        #exit(rs.error_code)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    return result

def get_all_stock(date):
    #### 获取证券信息 ####
    rs = bs.query_all_stock(day=date)
    if rs.error_code != '0':
        print('query_history_k_data_plus respond error_code:%d, error_msg: %s' % (rs.error_code, rs.error_msg))
        #exit(rs.error_code)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    return result

# 获取指定日期的指数、股票数据
def download_all_stock_data(date):
    bs.login()

    # 创建下载目录
    path = ".\\stock_data\\day_line"
    if not os.path.exists(path):
        os.makedirs(path)

    stock_rs = bs.query_all_stock(date)
    stock_df = stock_rs.get_data()
    for code in stock_df["code"]:
        print("Downloading: " + code)
        # 获取数据
        day_line = get_day_line(code, '1990-07-01', '')
        # 将数据输出到文件
        if not day_line.empty:
            day_line.to_csv("%s\\%s.csv" % (path, code), index=False)

    bs.logout()

def main():
    download_all_stock_data('2023-01-20')

if __name__ == '__main__':
    main()
