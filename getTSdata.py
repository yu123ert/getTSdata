# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version: ??
@author: laofish
@contact: laofish@outlook.com
@site: http://www.laofish.com
@file: getTSdata
@time: 2018/11/26  14:58

取天软数据 以前做过感觉找不到了
-------------------------------------------------
@Change Activity:
                   2018/11/26:
-------------------------------------------------
"""
import pandas as pd
import numpy as np

import time


import matplotlib.pyplot as plt

import os
import sys

sys.path.append("C:\Program Files\Tinysoft\Analyse.NET")

import traceback

import pickle
import datetime

# from WindPy import *

# 实际上我有这个模块的，但是pycharm找不到，我也没办法
import TSLPy3 as ts

ts.DefaultConnectAndLogin("test") #调用函数登陆


def tsbytestostr(data):
    "把gbk的字符转化为uft的字符"

    if (isinstance(data, (tuple)) or isinstance(data, (list))):
        lendata = len(data)
        ret = []
        for i in range(lendata):
            ret.append(tsbytestostr(data[i]))
    elif isinstance(data, (dict)):
        lendata = len(data)
        ret = {}
        for i in data:
            ret[tsbytestostr(i)] = tsbytestostr(data[i])
    elif isinstance(data, (bytes)):
        ret = data.decode('gbk')
    else:
        ret = data
    return ret


def tostry(data):
    ret = ""
    if isinstance(data, (int, float)):
        ret = "{0}".format(data)
    elif isinstance(data, (str)):
        ret = "\"{0}\"".format(data)
    elif isinstance(data, (list)):
        lendata = len(data)
        ret += "["
        for i in range(lendata):
            ret += tostry(data[i])
            if i < (lendata - 1):
                ret += ","
        ret += ']'
    elif isinstance(data, (tuple)):
        lendata = len(data)
        ret += "("
        for i in range(lendata):
            ret += tostry(data[i])
            if i < (lendata - 1):
                ret += ","
        ret += ')'
    elif isinstance(data, (dict)):
        it = 0
        lendata = len(data)
        ret += "{"
        for i in data:
            ret += tostry(i) + ":" + tostry(data[i])
            it += 1
            if it < lendata:
                ret += ","
        ret += "}"
    else:
        ret = "{0}".format(data)
    return ret


def getTSdata(sdate, stockID, cy):
    '''通过天软获取高频数据，只提取某一日的数据'''

    d2 = ts.RemoteCallFunc('MyGetTimeSeries', [sdate, sdate, stockID, cy], {})

    if d2[0] == 0:
        return d2[1]
    else:
        print(d2[2])


def getTSdate(sdate, edate):
    '''获取天软日期'''

    d3 = ts.RemoteCallFunc('MarketTradeDayQk', [sdate, edate], {})
    if d3[0] == 0:
        return d3[1]
    else:
        print(d3[2])


def getTSdata_day(sdate, edate, stockID, cy):
    '''通过天软获取日线'''

    d2 = ts.RemoteCallFunc('MyGetTimeSeries', [sdate, edate, stockID, cy], {})

    if d2[0] == 0:
        return d2[1]
    else:
        print(d2[2])


# 搞成天软格式的时间
# 起始日
sdate = ts.EncodeDate(2017, 6, 4)
# 终止日
edate = ts.EncodeDate(2018, 6, 4)

# 天软时间变正常时间
# ts.DecodeDate(43200)