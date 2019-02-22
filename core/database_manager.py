#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/18'
"""

import datetime
import os

from pymongo import MongoClient


class DBManager:
    def __init__(self, table_name):
        self.client = MongoClient("127.0.0.1", 27017)
        self.db = self.client["em_tk_database"]
        self.table = self.db[table_name]

    def clsoe_db(self):
        self.client.close()

    # 获取股票代码列表(sz格式)
    def get_code_list(self):
        return self.table.find({}, {"ticker": 1}, no_cursor_timeout=True)

    # 查询多条数据
    def find_by_key(self, request=None):
        if request is None:
            request = {}
        return self.table.find(request)

    # 查询单条数据
    def find_one_by_key(self, request=None):
        if request is None:
            request = {}
        return self.table.find_one(request)

    # 添加单条数据
    def add_one(self, post, created_time=datetime.datetime.now()):
        # 添加一条数据
        post['created_time'] = created_time
        return self.table.insert_one(post)

    # 添加历史交易记录
    def add_tk_item(self, ticker, __dict):
        return self.table.update_one({'ticker': ticker}, {"$push": {"data_list": __dict}})


base_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/data/data_code.txt"

# 初始化数据库表结构(首次运行时)
# if __name__ == "__main__":
#     dm = DBManager("em_pe_database")
#     __file = open(base_path, "r", encoding="utf-8")
#     tk_list = list()
#     while True:
#         line = __file.readline()
#         if '' == line:
#             break
#         str_code = line.split()[0]
#         str_name = line.split()[1]
#         if "XSHE" in str_code:
#             ticker = "sz." + str_code[:6]
#         elif "XSHG" in str_code:
#             ticker = "sh." + str_code[:6]
#         dm.add_one({"ticker": ticker, "name": str_name, "data_list": []})
