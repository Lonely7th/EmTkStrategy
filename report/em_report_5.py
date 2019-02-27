#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/26'
"""
import numpy as np
import matplotlib.pyplot as plt

from core.core_strategy import get_w_macd
from core.database_manager import DBManager


if __name__ == "__main__":
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

        # 数据计算
        close_list = [float(x["close"]) for x in tk_data_list if x["close"] != ""]
        open_list = [float(x["open"]) for x in tk_data_list if x["close"] != ""]
        max_list = [float(x["high"]) for x in tk_data_list if x["close"] != ""]
        low_list = [float(x["low"]) for x in tk_data_list if x["close"] != ""]
        volume_list = [float(x["volume"]) for x in tk_data_list if x["close"] != ""]
        wmacd_list, diff_list, dea_list = get_w_macd(close_list)

        for index in range(24, len(close_list) - 1):
            if wmacd_list[index] > 0 > wmacd_list[index - 1] and 0.1 >= diff_list[index] > 0:
                if np.mean(volume_list[index-5:index]) < volume_list[index]:
                    profit = (close_list[index + 1] - open_list[index + 1]) / open_list[index + 1]
                    pettm = float(pe_data_list[index]["peTTM"])
                    if -100 < pettm < 100:
                        result_list.append({"pr": profit, "pe": pettm})

    # print(len(result_list))
    # print(len([x for x in result_list if x["pr"]]))
    # print(len([x for x in result_list if not x["pr"]]))
    # print(len([x for x in result_list if x["pr"]]) / len(result_list))

    plt.subplot(111)
    lable_x = [x["pr"] for x in result_list]
    lable_y = [x["pe"] for x in result_list]
    plt.scatter(lable_x, lable_y, color="r")
    plt.grid(True)
    plt.show()
