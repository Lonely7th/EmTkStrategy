#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/18'
"""
from time import sleep

import baostock as bs

from core.database_manager import DBManager
from log.log_manager import Logger

'''
date	交易所行情日期	格式：YYYY-MM-DD
code	证券代码	格式：sh.600000。sh：上海，sz：深圳
open	今开盘价格	精度：小数点后4位；单位：人民币元
high	最高价	精度：小数点后4位；单位：人民币元
low	最低价	精度：小数点后4位；单位：人民币元
close	今收盘价	精度：小数点后4位；单位：人民币元
volume	成交数量	单位：股
amount	成交金额	精度：小数点后4位；单位：人民币元
adjustflag	复权状态	不复权、前复权、后复权
turn	换手率	精度：小数点后6位；单位：%
pctChg	涨跌幅	精度：小数点后6位
'''


def start_tk_crawl():
    global dm, log
    log = Logger()
    dm = DBManager("em_tk_database")

    log.logger.info("开始更新股票数据")
    bs.login()
    code_list = dm.get_code_list()
    for item in code_list:
        ticker = item["ticker"]
        max_try = 8
        for tries in range(max_try):
            rs = bs.query_history_k_data(ticker, "date,code,open,high,low,close,volume,amount,adjustflag,turn,"
                                                 "pctChg", frequency="w", adjustflag="3")
            if rs.error_code == '0':
                parse_pager(rs, ticker)
                break
            elif tries < (max_try - 1):
                sleep(2)
                continue
            else:
                log.logger.error("更新股票数据失败：" + str(ticker))
    log.logger.info("结束更新股票数据")
    bs.logout()


def parse_pager(content, ticker):
    timer_list = [x["date"] for x in dm.find_one_by_key({"ticker": ticker})["data_list"]]
    while content.next():
        item_row = content.get_row_data()
        __dict = {
            "date": item_row[0],
            "code": item_row[1],
            "open": item_row[2],
            "high": item_row[3],
            "low": item_row[4],
            "close": item_row[5],
            "volume": item_row[6],
            "amount": item_row[7],
            "adjustflag": item_row[8],
            "turn": item_row[9],
            "pctChg": item_row[10]
        }
        if __dict["date"] not in timer_list:
            dm.add_tk_item(ticker, __dict)
