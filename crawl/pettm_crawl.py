#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/19'
"""
from time import sleep

import baostock as bs

from core.database_manager import DBManager
from log.log_manager import Logger


def start_pe_crawl():
    global dm, log
    log = Logger()
    dm = DBManager("em_pe_database")

    log.logger.info("开始更新指数数据")
    bs.login()
    code_list = dm.get_code_list()
    for item in code_list:
        ticker = item["ticker"]
        max_try = 8
        for tries in range(max_try):
            rs = bs.query_history_k_data(ticker, "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM", frequency="d", adjustflag="2")
            if rs.error_code == "0":
                parse_pager(rs, ticker)
                break
            elif tries < (max_try - 1):
                sleep(2)
                continue
            else:
                log.logger.error("更新股票指数数据：" + str(ticker))
    log.logger.info("结束更新指数数据")
    bs.logout()


def parse_pager(content, ticker):
    timer_list = [x["date"] for x in dm.find_one_by_key({"ticker": ticker})["data_list"]]
    while content.next():
        item_row = content.get_row_data()
        __dict = {
            "date": item_row[0],
            "code": item_row[1],
            "close": item_row[2],
            "peTTM": item_row[3],
            "pbMRQ": item_row[4],
            "psTTM": item_row[5],
            "pcfNcfTTM": item_row[6]
        }
        if __dict["date"] not in timer_list:
            dm.add_tk_item(ticker, __dict)


if __name__ == "__main__":
    start_pe_crawl()
