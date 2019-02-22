#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/21'
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
            if wmacd_list[index] > wmacd_list[index - 1] > 0 >= wmacd_list[index - 2]:
                if (close_list[index] - open_list[index]) / open_list[index] > 0.1:
                    if float(pe_data_list[index]["peTTM"]) < 20:
                        result_list.append([open_list[index + 1], max_list[index + 1], close_list[index + 1], low_list[index + 1]])

    bar_list = list()
    for item in result_list:
        result = (item[1] - item[0]) / item[0]
        if result >= 0.02:
            bar_list.append((item[3] - item[0]) / item[0])
        # else:
        #     bar_list.append((item[2] - item[0]) / item[0])

    print(len(bar_list))
    print(len([x for x in bar_list if x >= 0]))
    print(len([x for x in bar_list if x < 0]))
    print(len([x for x in bar_list if x >= 0]) / len(bar_list))

    plt.subplot(111)
    lable_x = np.arange(len(bar_list))
    plt.bar(lable_x, bar_list, color="r", linewidth=1.0, linestyle="-")
    plt.xlim(lable_x.min(), lable_x.max() * 1.1)
    plt.ylim(min(bar_list) * 0.9, max(bar_list) * 1.1)
    plt.grid(True)
    plt.show()
