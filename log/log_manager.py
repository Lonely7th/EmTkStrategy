#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/20'
"""
import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }

    def __init__(self,filename='operation_log.log',level='info',when='D',back_count=12,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)

        if not self.logger.handlers:
            format_str = logging.Formatter(fmt)  # 设置日志格式
            self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
            sh = logging.StreamHandler()  # 往屏幕上输出
            sh.setFormatter(format_str)  # 设置屏幕上显示的格式
            th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=back_count,
                                                   encoding='utf-8')
            # 实例化TimedRotatingFileHandler
            # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
            # S 秒
            # M 分
            # H 小时
            # D 天
            # W 每星期（interval==0时代表星期一）
            # midnight 每天凌晨
            th.setFormatter(format_str)  # 设置文件里写入的格式
            self.logger.addHandler(sh)  # 把对象加到logger里
            self.logger.addHandler(th)
