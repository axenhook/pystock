# 获取股票的实时价格
from urllib.request import urlopen # python自带爬虫库
import pandas as pd
pd.set_option('expand_frame_repr', False) # 当列太多时不换行
pd.set_option('display.max_rows', 5000)   # 最多显示数据的行数

# ====神奇的网址
# 返回指定股票的数据：http://hq.sinajs.cn/list=sh600000,sz000002,sz300001
# 正常网址：https://finance.sina.com.cn/realstock/company/sh600000/nc.shtml

# ====构建网址
stock_code_list = ['s_sh600000', 's_sz000002', 's_sh600002', 's_h000003', 's_sz300123']
url = "http://hq.sinajs.cn/rn=1672628899212&list=" + ",".join(stock_code_list)
#print(url)
#exit(0)

# ====抓取数据
content = urlopen(url).read().decode('gbk')
print(content)

# ====将数据转换成DataFrame
content = content.strip() # 去掉文本前后的空格、回车等
data_line = content.split('\n')  # 每行是一个股票的数据
data_line = [i.replace('var hq_str_', '').split(',') for i in data_line]
df = pd.DataFrame(data_line, dtype='float')

# ====对DataFrame进行整理
df[0] = df[0].str.split('="')
df['stock_code'] = df[0].str[0].strip()
df['stock_name'] = df[0].str[-1].strip()
df['candle_end_time'] = df[30] + ' ' + df[31]  # 股票市场的k线，是普遍以当前K线结束时间来命名的
rename_dict = {1: 'open', 2: 'pre_closed', 3: 'closed', 4: 'high', 5: 'low', 6: 'buy1', 7: 'sell1',
               8: 'amount', 9: 'volume', 32: 'status'} # 自己去对比数据，会有新的发现
# 其中amount单位是股，volume单位是元
df.rename(columns=rename_dict, inplace=True)
df['status'] = df['status'].str.strip('";')
df = df[['stock_code', 'stock_name', 'candle_end_time', 'open', 'high', 'low', 'closed',
         'pre_closed', 'buy1', 'sell1', 'status']]

# ====考察退市、停牌股票
# 根据特征删除股票数据
df = df[df['open'] - 0 > 0.00001]

# ====考察新上市的股票
# 对于新上市的股票，pre_close指的是发行价

# ====考察除权股票
# 对于今天除权的股票，pre_close不是昨天真正的收盘价，而是交易所计算出来且公布的昨天的收盘价
# 有了这个数据，才能算出这个股票真正的涨跌幅


