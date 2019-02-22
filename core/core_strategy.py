#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/18'
"""
import datetime
import json

import numpy as np


from core.database_manager import DBManager
from core.report_manager import creat_report


# 计算当前时间段的wmacd值
from log.log_manager import Logger


def get_w_macd(price_list):
    ema_12_list = list()
    for index in range(len(price_list)):
        if index == 0:
            ema_12_list.append(price_list[0])
        else:
            ema_12_list.append(round(ema_12_list[index - 1] * 11 / 13 + price_list[index] * 2 / 13, 4))
    ema_26_list = list()
    for index in range(len(price_list)):
        if index == 0:
            ema_26_list.append(price_list[0])
        else:
            ema_26_list.append(round(ema_26_list[index - 1] * 25 / 27 + price_list[index] * 2 / 27, 4))
    diff_list = list()
    for index in range(len(ema_12_list)):
        diff = ema_12_list[index] - ema_26_list[index]
        diff_list.append(diff)
    dea_list = list()
    for index in range(len(diff_list)):
        if index == 0:
            dea_list.append(diff_list[0])
        else:
            dea_list.append(round(dea_list[index - 1] * 0.8 + diff_list[index] * 0.2, 4))
    wmacd_list = list()
    for index in range(len(dea_list)):
        bar = (diff_list[index] - dea_list[index]) * 3
        wmacd_list.append(bar)
    return wmacd_list, diff_list, dea_list


def fun_analysis(cur_time=datetime.datetime.now()):
    log = Logger()
    log.logger.info("开始分析数据")

    # 数据获取
    dm_tk = DBManager("em_tk_database")
    dm_pe = DBManager("em_pe_database")
    code_list = [x for x in dm_tk.get_code_list()]

    result_list = list()
    # 数据遍历
    for item in code_list:
        tk_item = dm_tk.find_one_by_key({"ticker": item["ticker"]})
        pe_item = dm_pe.find_one_by_key({"ticker": item["ticker"]})

        tk_data_list = tk_item["data_list"]
        pe_data_list = pe_item["data_list"]

        # 数据校验
        if str(cur_time).split(" ")[0] == str(pe_data_list[-1]["date"]) == str(tk_data_list[-1]["date"]):
            # 数据计算
            close_list = [float(x["close"]) for x in tk_data_list if x["close"] != ""]
            volume_list = [float(x["volume"]) for x in tk_data_list if x["close"] != ""]
            wmacd_list, diff_list, dea_list = get_w_macd(close_list)

            # 处理核心逻辑
            if wmacd_list[-1] > 0 >= wmacd_list[-2]:
                if np.mean(volume_list[-5:-1]) < volume_list[-1] and diff_list[-1] >= 0:
                    result_list.append({"ticker": item["ticker"], "diff": round(diff_list[-1], 4), "pe": float(pe_data_list[-1]["peTTM"])})
        else:
            log.logger.error("数据校验失败：" + str(item["ticker"]))

    print(result_list)
    log.logger.info("结束分析数据：" + json.dumps(result_list))

    # 生成分析报告
    creat_report(result_list)


if __name__ == "__main__":
    fun_analysis()
