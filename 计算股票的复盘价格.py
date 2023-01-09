# 根据预测者网的历史数据，计算复权价格

import pandas as pd
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)   # 最多显示数据的行数


def calculate_stock_price(df):
    # ====计算复权涨跌幅
    df['涨跌幅'] = df['收盘价'] / df['前收盘价'] - 1
    # print(df[['交易日期', '收盘价', '前收盘价', '涨跌幅']])

    # ====计算复权因子：假设你一开始有1元钱，投资到这个股票，最终会变成多少钱
    df['复权因子'] = (1 + df['涨跌幅']).cumprod()
    # print(df[['交易日期', '收盘价', '前收盘价', '涨跌幅', '复权因子']])

    # ====计算后复权价
    df['收盘价_复权'] = df['复权因子'] * (df.iloc[0]['收盘价'])
    # print(df[['交易日期', '收盘价', '前收盘价', '涨跌幅', '复权因子', '收盘价_复权']])

    # ====计算复权的开盘价、最高价、最低价
    df['开盘价_复权'] = df['开盘价'] / df['收盘价'] * df['收盘价_复权']
    df['最高价_复权'] = df['最高价'] / df['收盘价'] * df['收盘价_复权']
    df['最低价_复权'] = df['最低价'] / df['收盘价'] * df['收盘价_复权']
    return df

# ====导入数据


def main():
    path = '..\\stock_data\\sz000001.csv'
    df = pd.read_csv(path, encoding='gbk', skiprows=1)
    df = calculate_stock_price(df)

    print(df)


if __name__ == '__main__':
    main()
