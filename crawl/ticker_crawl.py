#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/22'
"""
from time import sleep

import baostock as bs

from core.database_manager import DBManager

'''
date	交易所行情日期	
code	证券代码	
open	开盘价	
high	最高价	
low	    最低价	
close	收盘价	
preclose	前收盘价	见表格下方详细说明
volume	成交量（累计 单位：股）	
amount	成交额（单位：人民币元）	
adjustflag	复权状态(1：后复权， 2：前复权，3：不复权）	
turn	换手率	[指定交易日的成交量(股)/指定交易日的股票的流通股总股数(股)]*100%
tradestatus	交易状态(1：正常交易 0：停牌）	
pctChg	涨跌幅（百分比）	日涨跌幅=[(指定交易日的收盘价-指定交易日前收盘价)/指定交易日前收盘价]*100%
peTTM	滚动市盈率	(指定交易日的股票收盘价/指定交易日的每股盈余TTM)=(指定交易日的股票收盘价*截至当日公司总股本)/归属母公司股东净利润TTM
pbMRQ	市净率	(指定交易日的股票收盘价/指定交易日的每股净资产)=总市值/(最近披露的归属母公司股东的权益-其他权益工具)
psTTM	滚动市销率	(指定交易日的股票收盘价/指定交易日的每股销售额)=(指定交易日的股票收盘价*截至当日公司总股本)/营业总收入TTM
pcfNcfTTM	滚动市现率	(指定交易日的股票收盘价/指定交易日的每股现金流TTM)=(指定交易日的股票收盘价*截至当日公司总股本)/现金以及现金等价物净增加额TTM
isST	是否ST股，1是，0否	
'''


def start_tk_crawl():
    global dm
    dm = DBManager("history_k_data")

    # 初始化baostock
    bs.login()
    # 获取股票代码列表
    code_list = dm.get_code_list()
    for item in code_list:
        max_try = 8  # 失败重连次数
        ticker = item["ticker"]
        print("开始加载股票数据：" + str(ticker))
        for tries in range(max_try):
            rs = bs.query_history_k_data_plus(ticker, "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                              start_date='2008-01-01', end_date='2019-05-31', frequency="d", adjustflag="3")
            if rs.error_code == '0':
                parse_pager(rs, ticker)  # 解析数据
                break
            elif tries < (max_try - 1):
                sleep(2)
                continue
            else:
                print("加载股票数据失败：" + str(ticker))
    print("加载股票数据完成")
    bs.logout()


# 解析数据并保存到数据库
def parse_pager(content, ticker):
    __list = list()
    while content.next():
        item_row = content.get_row_data()
        __dict = {
            "date": item_row[0],
            "code": item_row[1],
            "open": item_row[2],
            "high": item_row[3],
            "low": item_row[4],
            "close": item_row[5],
            "preclose": item_row[6],
            "volume": item_row[7],
            "amount": item_row[8],
            "adjustflag": item_row[9],
            "turn": item_row[10],
            "tradestatus": item_row[11],
            "pctChg": item_row[12],
            "isST": item_row[13]
        }
        __list.append(__dict)
    dm.add_tk_item(ticker, __list)
    __list.clear()


if __name__ == "__main__":
    start_tk_crawl()
