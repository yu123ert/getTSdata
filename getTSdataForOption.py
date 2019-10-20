# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version: ??
@author: laofish
@contact: laofish@outlook.com
@site: http://www.laofish.com
@file: getTSdataForOption
@time: 2019/6/22  14:58
-------------------------------------------------
@Change Activity:
                   2019/6/22:
                   获取天软期权数据
-------------------------------------------------
"""


import pandas as pd
import numpy as np

import time
import math

from dateutil.parser import parse

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# import matplotlib.finance as mpf

import sys
sys.path.append("D:\Program Files\Tinysoft\Analyse.NET")

import TSLPy3 as ts

import traceback

import pickle
from datetime import datetime

# from WindPy import *

def tsbytestostr(data):
    "把gbk的字符转化为uft的字符"

    # 不破坏数组结构，将数组中的中文解码显示出来

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


def getTSdata_optionchain(stockID,endt):

    '''通过天软自定义函数，获取期权基础信息'''

    d4=ts.RemoteCallFunc('getOptionChain',[stockID,endt],{})

    if d4[0] == 0:
        # #data[0]==0 表示成功,data[1] 运行结果,
        # Data[2] 如果错误的错误信息
        return d4[1]
    else:
        print(d4[2])


def getTSdata_optionchain_pub(stockID,endt):

    '''通过天软公共函数，获取期权基础信息'''

    d4=ts.RemoteCallFunc('OP_GetOptionChain',[stockID,endt],{})

    if d4[0] == 0:
        # #data[0]==0 表示成功,data[1] 运行结果,
        # Data[2] 如果错误的错误信息
        return d4[1]
    else:
        print(d4[2])


def getTS_optClose(stockID, endt):
    '''获取收盘价数据,把代码获取放在天软函数中进行
    能在天软中的，尽量在天软中完成

       ret2:=OP_GetOptionChain(StockID,endt) ;
       //获取期权基础信息

       //选中数组某列
       ret:=select['StockID'] from ret2 end  ;

       天软这一段很重要
    '''

    d5=ts.RemoteCallFunc('getOptionPriceDayArray',[stockID, endt],{})

    if d5[0] == 0:
        # #data[0]==0 表示成功,data[1] 运行结果,
        # Data[2] 如果错误的错误信息
        return d5[1]
    else:
        print(d5[2])


# 搞成天软格式的时间
# 起始日
sdate = ts.EncodeDate(2015, 2, 9)
# 终止日
edate = ts.EncodeDate(2019, 6, 20)



# 天软时间变正常时间
# ts.DecodeDate(43200)

# 存储最终结果
df = pd.DataFrame()

# 获取交易日序列
dateS = getTSdate(sdate, edate)

stockID="SH510050" # 天软代码


# 解析结果的list
optID=[] # 当日期权代码
optDate=[] # 交易日
optOpen=[] # 开盘价
optClose=[] # 收盘价

# indexcode = 'CSIH30402'  # 500股息点
# cy2 = '日线'
#
# # 获取连续数据
# d5 = getTSdata_day(sdate, edate, indexcode, cy2)

try:
    for tdate in dateS:

        print(ts.DecodeDate(tdate))

        optionInfo=getTS_optClose(stockID, tdate)

        # optionInfo = getTSdata_optionchain_pub(stockID, tdate)

        # att decode 解析天软的中文，不破坏列表结构
        data2 = tsbytestostr(optionInfo)

        for element in data2:

            optDate.append(element['日期'])
            optID.append(element['StockID'])

            optOpen.append(element['开盘价'])

            optClose.append(element['收盘价'])

            # OP_GetMarcketData(ret, endT)

    df['date']=optDate
    df['optID']=optID
    df['close']=optClose
    df['open']=optOpen

    f1 = open('Optiondata_raw' + '.pkl', 'wb')
    pickle.dump(df, f1, True)
    f1.close()

    # f3 = open('Optiondata_raw' + '.pkl', 'rb')
    # totaldf = pickle.load(f3)
    # f3.close()

    df.to_excel('optdata.xlsx')


















except Exception as e:
    s = sys.exc_info()
    print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
    print("Unexpected Error: {}".format(e))
    traceback.print_exc()