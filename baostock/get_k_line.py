# ��baostock.com������ʷ����
import baostock as bs
import pandas as pd
import os

#### ��ȡ����A����ʷK������ ####
# ��ϸָ��������μ�����ʷ����ָ��������½ڣ��������ߡ������롰���ߡ�������ͬ���������ߡ�������ָ����
# ������ָ�꣺date,time,code,open,high,low,close,volume,amount,adjustflag
# ������ָ�꣺date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
# ��������˵��
# ��������	��������	�㷨˵��
# date	��������������	
# code	֤ȯ����	
# open	���̼�	
# high	��߼�	
# low	��ͼ�	
# close	���̼�	
# preclose	ǰ���̼�	������·���ϸ˵��
# volume	�ɽ������ۼ� ��λ���ɣ�	
# amount	�ɽ����λ�������Ԫ��	
# adjustflag	��Ȩ״̬(1����Ȩ�� 2��ǰ��Ȩ��3������Ȩ��	
# turn	������	[ָ�������յĳɽ���(��)/ָ�������յĹ�Ʊ����ͨ���ܹ���(��)]*100%
# tradestatus	����״̬(1���������� 0��ͣ�ƣ�	
# pctChg	�ǵ������ٷֱȣ�	���ǵ���=[(ָ�������յ����̼�-ָ��������ǰ���̼�)/ָ��������ǰ���̼�]*100%
# peTTM	������ӯ��	(ָ�������յĹ�Ʊ���̼�/ָ�������յ�ÿ��ӯ��TTM)=(ָ�������յĹ�Ʊ���̼�*�������չ�˾�ܹɱ�)/����ĸ��˾�ɶ�������TTM
# pbMRQ	�о���	(ָ�������յĹ�Ʊ���̼�/ָ�������յ�ÿ�ɾ��ʲ�)=����ֵ/(�����¶�Ĺ���ĸ��˾�ɶ���Ȩ��-����Ȩ�湤��)
# psTTM	����������	(ָ�������յĹ�Ʊ���̼�/ָ�������յ�ÿ�����۶�)=(ָ�������յĹ�Ʊ���̼�*�������չ�˾�ܹɱ�)/Ӫҵ������TTM
# pcfNcfTTM	����������	(ָ�������յĹ�Ʊ���̼�/ָ�������յ�ÿ���ֽ���TTM)=(ָ�������յĹ�Ʊ���̼�*�������չ�˾�ܹɱ�)/�ֽ��Լ��ֽ�ȼ��ﾻ���Ӷ�TTM
# isST	�Ƿ�ST�ɣ�1�ǣ�0��	
def get_day_line(code, start, end):
    # ͨ��API�ӿڻ�ȡA����ʷ�������ݣ�����ͨ���������û�ȡ��k�ߡ���k�ߡ���k�ߣ��Լ�5���ӡ�15���ӡ�30���Ӻ�60����k�����ݣ��ʺϴ���������ݽ���ѡ�ɺͷ�����
    # �ܻ�ȡ1990-12-19����ǰʱ������ݣ�
    # �ɲ�ѯ����Ȩ��ǰ��Ȩ����Ȩ���ݡ�
    # �������壺
    # code����Ʊ���룬sh��sz.+6λ���ִ��룬����ָ�����룬�磺sh.601398��sh���Ϻ���sz�����ڡ��˲�������Ϊ�գ�
    # fields��ָʾ��ƣ�֧�ֶ�ָ�����룬�԰�Ƕ��ŷָ�����д������Ϊ�������͵��С���ϸָ���б����ʷ����ָ������½ڣ�����������߲�����ͬ���˲�������Ϊ�գ�
    # start����ʼ���ڣ�����������ʽ��YYYY-MM-DD����Ϊ��ʱȡ2015-01-01��
    # end���������ڣ�����������ʽ��YYYY-MM-DD����Ϊ��ʱȡ���һ�������գ�
    # frequency���������ͣ�Ĭ��Ϊd����k�ߣ�d=��k�ߡ�w=�ܡ�m=�¡�5=5���ӡ�15=15���ӡ�30=30���ӡ�60=60����k�����ݣ������ִ�Сд��ָ��û�з��������ݣ�����ÿ�����һ�������ղſ��Ի�ȡ������ÿ�����һ�������ղſ��Ի�ȡ��
    # adjustflag����Ȩ���ͣ�Ĭ�ϲ���Ȩ��3��1����Ȩ��2��ǰ��Ȩ����֧�ַ����ߡ����ߡ����ߡ�����ǰ��Ȩ�� BaoStock�ṩ�����ǵ�����Ȩ�㷨��Ȩ���ӣ�������ܼ�����Ȩ���Ӽ�����BaoStock��Ȩ���Ӽ�顣
    rs = bs.query_history_k_data_plus(code,
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        start_date=start, end_date=end,
        frequency="d", adjustflag="3")
    if rs.error_code != '0':
        print('query_history_k_data_plus respond error_code:%s, error_msg: %s' % (rs.error_code, rs.error_msg))
        #exit(rs.error_code)
    
    #### ��ӡ����� ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # ��ȡһ����¼������¼�ϲ���һ��
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
    
    #### ��ӡ����� ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # ��ȡһ����¼������¼�ϲ���һ��
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    
    return result

def get_all_stock(date):
    #### ��ȡ֤ȯ��Ϣ ####
    rs = bs.query_all_stock(day=date)
    if rs.error_code != '0':
        print('query_history_k_data_plus respond error_code:%d, error_msg: %s' % (rs.error_code, rs.error_msg))
        #exit(rs.error_code)
    
    #### ��ӡ����� ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # ��ȡһ����¼������¼�ϲ���һ��
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    
    return result

# ��ȡָ�����ڵ�ָ������Ʊ����
def download_all_stock_data(date):
    bs.login()
    
    # ��������Ŀ¼
    path = ".\\stock_data\\day_line"
    if not os.path.exists(path):
        os.makedirs(path)
    
    stock_rs = bs.query_all_stock(date)
    stock_df = stock_rs.get_data()
    for code in stock_df["code"]:
        print("Downloading: " + code)
        # ��ȡ����
        day_line = get_day_line(code, '1990-07-01', '')
        # ������������ļ�
        if not day_line.empty:
            day_line.to_csv("%s\\%s.csv" % (path, code), index=False)

    bs.logout()

def main():
    download_all_stock_data('2023-01-20')

if __name__ == '__main__':
    main()
