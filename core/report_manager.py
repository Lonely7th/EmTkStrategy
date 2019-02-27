#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'JN Zhang'
__mtime__ = '2019/2/18'
"""
import datetime
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import xlwt

from log.log_manager import Logger

base_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + "/report/doc/"


# 生成分析报告
def creat_report(content, created_time=datetime.datetime.now()):
    global log
    log = Logger()

    log.logger.info("开始生成报告")
    file_name = "report-" + str(created_time).split(" ")[0] + ".xls"
    file_path = base_path + file_name
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('sheet 1')
    # 设置报表样式
    style_normal = xlwt.XFStyle()  # 普通样式
    style_header = xlwt.XFStyle()  # 头部样式
    style_light = xlwt.XFStyle()  # 高亮样式

    al = xlwt.Alignment()
    al.horz = 0x02  # 设置水平居中
    al.vert = 0x01  # 设置垂直居中
    style_normal.alignment = al
    style_header.alignment = al
    style_light.alignment = al

    font = xlwt.Font()
    font.name = 'Times New Roman'
    font.bold = True  # 黑体
    style_header.font = font  # 设定样式

    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 0x1F
    style_light.pattern = pattern

    # 生成头部标签
    sheet.write(0, 0, 'TICKER', style_header)
    sheet.write(0, 1, 'DIFF', style_header)
    sheet.write(0, 2, 'PETTM', style_header)
    for index in range(len(content)):
        item = content[index]
        if item["pe"] <= 20 or item["diff"] <= 0.1:
            sheet.write(index+1, 0, item["ticker"], style_light)
            sheet.write(index+1, 1, item["diff"], style_light)
            sheet.write(index+1, 2, item["pe"], style_light)
        else:
            sheet.write(index + 1, 0, item["ticker"], style_normal)
            sheet.write(index + 1, 1, item["diff"], style_normal)
            sheet.write(index + 1, 2, item["pe"], style_normal)

    sheet.col(0).width = 4000
    sheet.col(1).width = 4000
    sheet.col(2).width = 4000
    wbk.save(file_path)
    log.logger.info("结束生成报告")

    send_report2mail(file_name, file_path)


# 发送报告到邮件
def send_report2mail(file_name=None, file_path=None):
    log.logger.info("开始发送邮件")

    sender = '1003882179@qq.com'
    receivers = ['1003882179@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header('EmTkStrategy', 'utf-8')
    message['To'] = Header('-', 'utf-8')
    subject = 'EmTkStrategy 周报'
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文内容
    message.attach(MIMEText('附件', 'plain', 'utf-8'))

    if file_path:
        log.logger.info("开始添加附件")
        att1 = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename=' + file_name
        message.attach(att1)

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.helo()
        server.ehlo()
        server.login("1003882179@qq.com", "qkeoioxuepsjbcha")
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        log.logger.info("邮件发送成功")
    except smtplib.SMTPException:
        log.logger.info("邮件发送失败")


if __name__ == "__main__":
    creat_report([])
