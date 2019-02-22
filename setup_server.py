#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/18'
"""
import multiprocessing
import threading
import datetime

from core.core_strategy import fun_analysis
from crawl.pettm_crawl import start_pe_crawl
from crawl.ticker_w_crawl import start_tk_crawl


def start_service():
    pool = multiprocessing.Pool(processes=2)
    # 启动数据接口
    # pool.apply_async()
    # 启动定时器
    pool.apply_async(fun_timer)
    pool.close()
    pool.join()


# 定时器(启动服务时调用)
def fun_timer():
    # 每分钟与系统进行对时
    cur_time = datetime.datetime.now().time()
    print(cur_time)
    hour = str(cur_time).split(":")[0]
    minute = str(cur_time).split(":")[1]
    # 每周五23点更新数据并生成分析报告
    if hour == "23" and minute == "01":
        if datetime.datetime.strptime(str(datetime.datetime.now().date()), "%Y-%m-%d").weekday() == 4:
            # 开始更新数据
            start_tk_crawl()
            start_pe_crawl()
            # 开始生成报告
            fun_analysis()

    global timer
    timer = threading.Timer(60, fun_timer)
    timer.start()


if __name__ == "__main__":
    start_service()
