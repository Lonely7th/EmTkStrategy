#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/26'
"""
import datetime
import json

import numpy as np
import matplotlib.pyplot as plt

from core.core_strategy import get_w_macd
from core.database_manager import DBManager
from log.log_manager import Logger

capital_base = 1000000
history_capital = list()


# 时间列表
def date_range(start, end, step=1, format="%Y-%m-%d"):
    strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
    days = (strptime(end, format) - strptime(start, format)).days + 1
    return [strftime(strptime(start, format) + datetime.timedelta(i), format) for i in range(0, days, step)]


if __name__ == "__main__":
    log = Logger()
    dm_tk = DBManager("em_tk_database")
    dm_pe = DBManager("em_pe_database")

    date_list_table = [date_range("2016-01-01", "2016-12-31"), date_range("2017-01-01", "2017-12-31"), date_range("2018-01-01", "2018-12-31")]
    code_list = [x for x in dm_tk.get_code_list()]

    for date_list in date_list_table:
        capital_base = 1000000
        history_capital = list()
        for index in range(len(date_list)):
            cur_date = date_list[index]
            if datetime.datetime.strptime(cur_date, "%Y-%m-%d").weekday() == 4:
                history_capital.append(capital_base)
                log.logger.info("current_time：" + str(cur_date))
                result_list = list()

                for item in code_list:
                    tk_item = dm_tk.find_one_by_key({"ticker": item["ticker"]})
                    pe_item = dm_pe.find_one_by_key({"ticker": item["ticker"]})

                    tk_data_list = [x for x in tk_item["data_list"] if datetime.datetime.strptime(x["date"], "%Y-%m-%d") < datetime.datetime.strptime(cur_date, "%Y-%m-%d")]

                    if len(tk_data_list) > 20:
                        # 数据计算
                        close_list = [float(x["close"]) for x in tk_data_list if x["close"] != ""]
                        open_list = [float(x["open"]) for x in tk_data_list if x["close"] != ""]
                        max_list = [float(x["high"]) for x in tk_data_list if x["close"] != ""]
                        low_list = [float(x["low"]) for x in tk_data_list if x["close"] != ""]
                        volume_list = [float(x["volume"]) for x in tk_data_list if x["close"] != ""]

                        pe_data_list = [x for x in pe_item["data_list"] if x["date"] == tk_data_list[-1]["date"]]
                        if pe_data_list and pe_data_list[0]["peTTM"]:
                            pe_data = float(pe_data_list[0]["peTTM"])
                            wmacd_list, diff_list, dea_list = get_w_macd(close_list)

                            if wmacd_list[-1] > 0 >= wmacd_list[-2]:
                                if np.mean(volume_list[-5:-1]) < volume_list[-1] and 0.1 >= diff_list[-1] >= 0:
                                    data = [x for x in dm_tk.find_one_by_key({"ticker": item["ticker"]})["data_list"] if x["date"] == cur_date]
                                    if data:  # 新增涨幅限制
                                        result_list.append(data[0])
                log.logger.info("result_list：" + json.dumps(result_list))

                # 计算结果
                if result_list:
                    capital = capital_base / len(result_list)
                    new_capital = 0
                    for item in result_list:
                        close_price = float(item["close"])
                        open_price = float(item["open"])
                        max_price = float(item["high"])

                        profit = (close_price - open_price) / open_price
                        new_capital += (capital * (1 + profit))
                    capital_base = new_capital

                log.logger.info("base_capital：" + str(capital_base))

        net_rate = (history_capital[-1] - history_capital[0]) / history_capital[0]  # 计算回测结果
        log.logger.info("total_profit：" + str(round(net_rate * 100, 2)) + "%")

        # 绘图
        plt.subplot(111)
        lable_x = np.arange(len(history_capital))
        plt.plot(lable_x, history_capital, color="r", linewidth=1.0, linestyle="-")
        plt.xlim(lable_x.min(), lable_x.max() * 1.1)
        plt.ylim(min(history_capital) * 0.9, max(history_capital) * 1.1)
        plt.grid(True)
        plt.show()
