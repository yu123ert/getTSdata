# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version: ??
@author: laofish
@contact: laofish@outlook.com
@site: http://www.laofish.com
@file: findExtremeHLstock
@time: 2019/10/20  14:58

这个研究课题，应该简化一下

--------------------------

日内涨跌5%以后，同方向还能再涨2%的可能性有多大
------------

即日内涨5%，最终收盘涨8%，即有3%的超额
--------------------------------------------------
日内跌5%，收盘跌8%，也是3%的超额

--------------------------------

同样的话题是，日内涨跌5%以后，同方向回来幅度有多大

-------------------------------------------------
@Change Activity:
                   2019/10/20:
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


def getTSdata_MyGetTimeSeriesLOHC(sdate, edate, stockID, cy):
    '''获取某只股票低开高收数据'''

    d2 = ts.RemoteCallFunc('MyGetTimeSeriesLOHC', [sdate, edate, stockID, cy], {})

    if d2[0] == 0:

        # #data[0]==0 表示成功,data[1] 运行结果,
        # Data[2] 如果错误的错误信息

        return d2[1]
    else:
        print(d2[2])


if __name__ == '__main__':


    cy= '日线'

    dfcode=pd.read_excel('stockcode.xlsx')

    stockcode=dfcode['代码'].tolist()

    # 搞成天软格式的时间
    # 起始日
    sdate = ts.EncodeDate(2017, 1, 1)
    # 终止日
    edate = ts.EncodeDate(2019, 10, 20)

    # 获取交易日序列
    dateS = getTSdate(sdate, edate)

    # 解析结果的list
    s2_close = []
    s2_low = []
    s2_datetime = []
    s2_high = []
    s2_code = []

    df2 = pd.DataFrame() # 整理所有数据

    for scode in stockcode:
        # 获取连续数据
        d5 = getTSdata_MyGetTimeSeriesLOHC(sdate, edate, scode, cy)
        # 转化为能看懂的数据
        data4 = tsbytestostr(d5)


        # 解析结果的list
        for element in data4:
            s2_datetime.append(element['时间日期'])
            s2_close.append(element['收盘价'])
            s2_high.append(element['最高价'])
            s2_code.append(scode)
            s2_low.append(element['最低价'])

    # 汇总统计数据
    df2['code'] = s2_code
    df2['close'] = s2_close
    df2['high'] = s2_high
    df2['low']=s2_low

    # pandas 可以直接将类似时间序列的东西，转为时间序列
    df2.index = pd.to_datetime(s2_datetime)

    #  att 把高频数据都存储下来
    f1 = open('stockExtremeHLdata' + '.pkl', 'wb')
    pickle.dump(df2, f1, True)
    f1.close()


    # 读取保存的数据
    # f3 = open('stockExtremeHLdata.pkl', 'rb')
    # totaldf = pickle.load(f3)
    # f3.close()




    pass


