#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/6/28'
"""
import xlwt

from core.database_manager import DBManager


resultList = list()


def isLimitUp(data1, data2):
    return round(float(data2["close"]) * 1.1, 2) == float(data1["close"])


def insertList(__list, index1, index2):
    resultList.append({"up": __list[index1: index2], "low": __list[index2: index2+5]})


# 设置表格样式
def set_style(name,height,bold=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font
    return style


def save2Excel():
    print(resultList)
    f = xlwt.Workbook()
    sheet1 = f.add_sheet("Sheet1", cell_overwrite_ok=True)
    row0 = ["date", "ticker", "volume1", "volume2",	"volume3", "volume4", "volume5", "volume6",	"pctChg1", "pctChg2", "pctChg3", "pctChg4", "pctChg5"]
    # 添加列标题
    for i in range(0, len(row0)):
        sheet1.write(0, i, row0[i], set_style('Times New Roman', 220, True))
    for index in range(len(resultList)):
        item = resultList[index]
        sheet1.write(index + 1, 0, item["up"][0]["date"])
        sheet1.write(index + 1, 1, item["up"][0]["code"])

        for __up in range(len(item["up"])):
            sheet1.write(index + 1, __up + 2, item["up"][__up]["volume"])

        for __low in range(len(item["low"])):
            sheet1.write(index + 1, __low + 8, item["low"][__low]["pctChg"])
    f.save('ts_data.xls')


if __name__ == "__main__":
    dm_tk = DBManager("history_k_data")

    code_list = dm_tk.get_code_list()

    for item in code_list:
        print(item["ticker"])
        tk_item = dm_tk.find_one_by_key({"ticker": item["ticker"]})
        data_list = tk_item["data_list"][0]
        limit_up_count = 0
        for index in range(1, len(data_list)-5):  # 取中段数据防止越界
            if isLimitUp(data_list[index], data_list[index-1]):
                limit_up_count += 1
                if limit_up_count == 6:
                    limit_up_count = 0
                    insertList(data_list, index-5, index+1)
            else:
                if limit_up_count >= 2:
                    insertList(data_list, index - limit_up_count, index)
                limit_up_count = 0
    save2Excel()
