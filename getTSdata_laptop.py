#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: laofish
@contact: laofish@outlook.com
@site: http://www.laofish.com
@file: tsdownload
@time: 2018-04-12 15:30

天软数据采集


update: 笔记本获得天软数据 2019/4/18

20191020 这个应该是研究 股指期货和现货的真正的升贴水的历史变化情况的（考虑指数分红后）,日内高频数据

"""

import pandas as pd
import numpy as np

import time
import math

from dateutil.parser import parse

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# import matplotlib.finance as mpf
import os
import sys

# sys.path.append('D:\Program Files\Tinysoft\Analyse.NET')
# sys.path.append('C:\Program Files\Tinysoft\Analyse.NET\LU')
sys.path.append('C:\\Program Files\\Tinysoft\\Analyse.NET\\')

import TSLPy3 as ts

import traceback

import pickle
from datetime import datetime

from WindPy import *

# 实际上我有这个模块的，但是pycharm找不到，我也没办法
# import TSLPy3 as ts


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

# stock1='IC01' # 天软里面的当月连续
# stock2='IC02' # 天软里面的次月连续
#


# 获取期货合约代码


# 周期

cy = '1分钟线'

# 获取交易日序列
dateS = getTSdate(sdate, edate)

s_price = []
s_datetime = []
s_vol = []
s_code = []

# 存储最终结果
df = pd.DataFrame()

# 提取次月合约
# 不合并在一起是不想把天软函数本身搞的太复杂

df2 = pd.DataFrame()

s2_price = []
s2_datetime = []
s2_vol = []
s2_code = []

try:

    # #=============================================
    # for tdate in dateS:
    #
    #     print(ts.DecodeDate(tdate))
    #
    #     fcode = ts.RemoteCallFunc('GetFuturesID', ['IC', tdate], {})
    #     fcode2 = tsbytestostr(fcode[1])
    #
    #     stock1 = fcode2[0]
    #
    #     data = getTSdata(tdate, stock1, cy)
    #
    #     # decode
    #     data2 = tsbytestostr(data)
    #
    #     # 解析结果的list
    #     for element in data2:
    #         s_datetime.append(element['t'])
    #         s_price.append(element['收盘价'])
    #         s_vol.append(element['成交量'])
    #         s_code.append(stock1)
    #
    #     # stock2
    #     stock2 = fcode2[1]
    #     data3 = getTSdata(tdate, stock2, cy)
    #
    #     # decode
    #     data4 = tsbytestostr(data3)
    #
    #     # 解析结果的list
    #     for element in data4:
    #         s2_datetime.append(element['t'])
    #         s2_price.append(element['收盘价'])
    #         s2_vol.append(element['成交量'])
    #         s2_code.append(stock2)
    #
    # df['price'] = s_price
    # df['volume'] = s_vol
    # df['code'] = s_code
    # # pandas 可以直接将类似时间序列的东西，转为时间序列
    # df.index = pd.to_datetime(s_datetime)
    #
    # df2['price'] = s2_price
    # df2['volume'] = s2_vol
    # df2['code'] = s2_code
    # # pandas 可以直接将类似时间序列的东西，转为时间序列
    # df2.index = pd.to_datetime(s2_datetime)
    #
    # totaldf = pd.merge(df, df2, how='inner', left_index=True, right_index=True,
    #                    suffixes=('_1', '_2'), copy=True, indicator=False,
    #                    validate=None)

    # # att 把高频数据都存储下来
    # f1 = open('HFICdata_raw' + '.pkl', 'wb')
    # pickle.dump(totaldf, f1, True)
    # f1.close()
    # #==============================================

    f3 = open('HFICdata_raw.pkl', 'rb')
    totaldf = pickle.load(f3)

    f3.close()

    # 计算当月期货和次月期货之间的分红
    # print(totaldf)

    indexcode = 'CSIH30402'  # 500股息点
    cy2 = '日线'

    # 获取连续数据
    d5 = getTSdata_day(sdate, edate, indexcode, cy2)
    # 转化为能看懂的数据
    d6 = tsbytestostr(d5)

    s3_date = []
    s3_price = []
    df3 = pd.DataFrame()

    for element in d6:
        s3_date.append(element['t'])
        s3_price.append(element['收盘价'])

    # 数据放到df里面，方便用
    df3['price'] = s3_price
    df3.index = pd.to_datetime(s3_date)

    # 天软的股息点数据有个问题在于
    # 他剔除了为零的股息
    # 这样数据会少一段，需要把缺少的数据补位0

    # step1 生成交易日序列
    datef = []
    for datenum in dateS:
        datetuple = ts.DecodeDate(datenum)
        datestr = str(datetuple[0]) + '-' + str(datetuple[1]) + '-' + str(datetuple[2])
        datef.append(parse(datestr))

    # step2 插入缺失的零
    for elm in datef:
        if elm not in df3.index:
            # index 必须用list 框起来
            tdf = pd.DataFrame([0], index=[elm], columns=['price'])
            # append不会修改原来的df，需要重新赋值一下
            df3=df3.append(tdf)

    # 重新按照索引排个序
    df3.sort_index(axis=0, level=None, ascending=True, inplace=True, kind='quicksort', na_position='last')

    # 计算每日分红
    df3['deltap'] = df3['price'] - df3['price'].shift(1)

    # 如果前一年到后一年，出现负值,修改为零
    # 以loc标签形式才可以修改 逻辑筛选出来的值
    df3.loc[df3['deltap'] < 0, 'deltap'] = 0

    # 得到一个累加值
    # df3里面有一个nan，这里做零处理
    df3['deltapcomsum'] = df3['deltap'].cumsum()

    # 期货到期日，用自己的excel表格数据
    dfepdate = pd.read_csv('ICexpiredate.csv', header=0)

    # 这是深度复制，不会出现df5=dfepdate[20:] 这种错误
    # df5[1,1]=0 A value is trying to be set on a copy of
    # a slice from a DataFrame.
    df4 = dfepdate[20:].copy()

    # 将合约到期日赋给totaldf
    # 前一个代码
    code1 = pd.unique(totaldf['code_1'])
    totaldf['expdate'] = np.nan
    for code in code1:
        # 如果筛选出来的是全量结果，实际上是无法赋值修改的 att 不是，可以修改全量结果，只是要用loc
        # totaldf[totaldf['code_1']==code]['expdate']= \ # 这样直接索引也不行
        totaldf.loc[totaldf['code_1'] == code, 'expdate'] = \
            dfepdate[dfepdate['Name'] == code]['lasttrade_date'].values[0]

    code2 = pd.unique(totaldf['code_2'])
    totaldf['expdate2'] = np.nan
    for code in code2:
        # 如果筛选出来的是全量结果，实际上是无法赋值修改的 att 不是，可以修改全量结果，只是要用loc
        # totaldf[totaldf['code_1']==code]['expdate']= \ # 这样直接索引也不行
        totaldf.loc[totaldf['code_2'] == code, 'expdate2'] = \
            dfepdate[dfepdate['Name'] == code]['lasttrade_date'].values[0]

    # 求两个到期日的分红差
    expdatelist = pd.unique(totaldf['expdate'])  # 字符串

    # lambda 方法
    # myf = lambda x: datetime.strptime(x, '%Y-%m-%d')
    # 列表表达式法

    # parse方法处理时间格式方便多了
    expdatelist2 = [parse(x) for x in expdatelist]

    # 把到期日搞成时间格式
    # lambda 方法
    myf = lambda x: parse(x)
    # apply方法，对元素使用
    totaldf['expdate_t'] = totaldf['expdate'].apply(myf)

    totaldf['fh1'] = np.nan

    for expd in expdatelist2:

        # loc这种形式标签可以
        if expd in df3.index:
            # totaldf['expdate'] 这里面是字符串
            totaldf.loc[totaldf['expdate_t'] == expd, 'fh1'] = \
                df3.loc[expd, 'deltapcomsum']

    expdatelist3 = pd.unique(totaldf['expdate2'])  # 字符串

    # lambda 方法
    # myf = lambda x: datetime.strptime(x, '%Y-%m-%d')
    # 列表表达式法
    # expdatelist4 = [datetime.strptime(x, '%Y-%m-%d') for x in expdatelist3]

    expdatelist4 = [parse(x) for x in expdatelist3]

    # 增加一个时间列维度
    totaldf['expdate2_t'] = totaldf['expdate2'].apply(myf)

    totaldf['fh2'] = np.nan

    for expd in expdatelist4:

        # loc这种形式标签可以
        if expd in df3.index:
            totaldf.loc[totaldf['expdate2_t'] == expd, 'fh2'] = \
                df3.loc[expd, 'deltapcomsum']

    # 期货分红差
    totaldf['fhcha'] = totaldf['fh2'] - totaldf['fh1']


    #########
    # 处理高频数据
    # 跨期收益
    # 多头展期，核心理论是对指数的增强收益
    # 应该是卖出当月，买入下月，但是当月和下月之间的分红，指数会自然回落
    # 因此这里面下月更低的收入要剔除
    kqsy = totaldf['price_1'] - totaldf['price_2'] - totaldf['fhcha']


    # 绘制连续的图线
    # 默认的图线是以时间为下标，这样导致周末和非工作时间白白占用了作图空间，
    # 导致图线比较奇怪
    kqsy2 = kqsy.dropna()

    # 转为纯数字 不使用时间标签画图
    valuelist=kqsy2.values

    plt.plot(valuelist)
    # 获取x轴的属性
    axis = plt.gca().xaxis
    # # 获得刻度的文本字符串
    # # 数字
    xlabel=[x.get_text() for x in axis.get_ticklabels()]
    #
    # 找到数字对应的日期
    xlabel2=[]
    for xl in xlabel:
        if xl!='':
            xnum=int(xl)
            if xnum <len(kqsy2):
                xl2 = kqsy2.index[xnum].strftime('%y-%m-%d')
                xlabel2.append(xl2)
        else:
            xlabel2.append('')

    # 获取当前图像
    ax = plt.gca()
    # 获取# 获得刻度的位置列表
    lc = ax.xaxis.get_ticklocs()

    # 固定坐标标签位置，这样缺点是放大图像后标签不能改变了
    axis.set_major_locator(ticker.FixedLocator(lc))
    # 将原来的数字标签替换为时间标签
    axis.set_major_formatter(ticker.FixedFormatter((xlabel2)))

    # 获得刻度线或者刻度标签之后，可以设置其各种属性，
    # 下面设置刻度线为绿色粗线，文本为红色并且旋转45度：
    # for label in axis.get_ticklabels():
    #     label.set_color("red")
    #     label.set_rotation(45)
    #     label.set_fontsize(16)

    #=====================

    df = kqsy2
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    x = math.floor(len(df.index) / 10)
    # 同样是固定了标签，无法实现标签随图片放大缩小变化
    # 但是这里的好处是处理的非常简单
    # 不需要给标签定位 没有了locator, 也没有formatter对象
    # 非常简单有效
    ax.set_xticklabels(df.index[::x], rotation=30)

    # ax.plot(df.values, alpha=0.9)


    #============================
    # 绘制蜡烛图


    totaldf['kqsy'] = kqsy

    # tf 和totaldf 不是同一片内存，不需要加inplace，加了是其他意思
    tf = totaldf.dropna()

    tf['date'] = tf.index
    myf2 = lambda x: datetime.date(x)
    tf['date1'] = tf['date'].apply(myf2)
    # grp = tf.groupby('date1')
    # 这个语法更纯粹
    grp2 = tf['kqsy'].groupby(tf['date1'])

    q10 = lambda x: x.quantile(.1)
    q25 = lambda x: x.quantile(.25)
    q75 = lambda x: x.quantile(.75)
    q90 = lambda x: x.quantile(.90)

    pdf = pd.DataFrame()
    pdf['10'] = grp2.apply(q10)
    pdf['25'] = grp2.apply(q25)
    pdf['75'] = grp2.apply(q75)
    pdf['90'] = grp2.apply(q90)

    #=====================================
    # 绘制蜡烛图
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)
    # 10是坐标轴标签的价格，即点和点之间隔10个
    ax.set_xticks(range(0, len(pdf.index), 10))
    # 这个就是标签了，标签和标签之间也隔十个
    # 这样操作结果就是标签很密集，但是可以缩放，看怎么选取了
    # 旋转30度是需要的
    ax.set_xticklabels(pdf.index[::10], rotation=30)
    # matplotlib.finance.candlestick2_ochl(ax,
    # opens, closes, highs, lows, width=4,
    # colorup='k', colordown='r', alpha=0.75
    mpf.candlestick2_ochl(ax, pdf['25'], pdf['75'], pdf['90'], pdf['10'],
                          width=0.5, colorup='r', colordown='green',
                          alpha=0.6)
    plt.grid()
    #=======================================

    # 绘制连线图
    # 主题
    plt.style.use('ggplot')
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(pdf.index, pdf['75'], color='c', label='75')
    ax.plot(pdf.index, pdf['25'], color='m', label='25')

    ax.legend()
    ax.grid()
    ax.grid(True)

































    # 把高频数据都存储下来
    f2 = open('HFICdata' + '.pkl', 'wb')
    pickle.dump(totaldf, f2, True)

    f2.close()

    pass


































except Exception as e:
    s = sys.exc_info()
    print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
    print("Unexpected Error: {}".format(e))
    traceback.print_exc()
    # traceback.print_exc(file=open('tb.txt', 'w+'))

# ts.DefaultConnectAndLogin("test") #调用函数登陆
#
# Close = ts.RemoteExecute("return close();",{"StockID":"SH000001"})
# #注意第二个参数为系统参数不可省略,但是可以为空{}
# Stockname = ts.RemoteCallFunc("stockname",["SH000001"],{});
# #注意第三个参数为系统参数,不可省略,但是可以为空{}
#
#
# tsstr="""
# Stocks:=
# "SZ000001;SZ000002;SZ000004;SZ000005;SZ000006;SZ000007;SZ000008;SZ000009;SZ
# 000010;SZ000011;SZ000012;SZ000014;SZ000016;SZ000017;SZ000018;SZ000019;SZ000
# 020";
# BegT := 20151001T;
# EndT := 20160531T;
# cy := '日线';
# BuyCond := @Cross(MA(Close(),10),MA(Close(),20))=1;
# SellCond := @Cross(MA(Close(),20),MA(CLose(),10))=1;
# return TSFL_PB_TechnicalIndicator(Stocks,BegT,EndT,cy,BuyCond,SellCond);
# """
# data = ts.RemoteExecute(tsstr,{})
# # print(tostry(data[1]))
#
# tsbytestostr(data[1])
# # print(tostry(data[1])) #tostry 函数代码参考附录,相关的编码也可以参考


# Function GetTimeSeriesSample(BegT,EndT,StockId,cycle);
# Begin
#   SetSysParam(pn_stock(),StockId);
#   SetSysParam(pn_cycle(),cycle);
#   EndT:=EndT+0.999;
#   N:=TradeDays(BegT,EndT);
#   SetSysparam(pn_date(),EndT);
#   return Nday(N,"t",datetimetostr(sp_time()),"收盘价",close(),'成交量',vol());
# End;
#
# RemoteCallFunc('tradedays',{datenum(2014,01,01)-693960,datenum(2014,06,01)-693960})
#
# ts.RemoteCallFunc('tradedays',{datenum(2014,01,01)-693960,datenum(2014,06,01)-693960})
#
# MyGetTimeSeries(BegT,EndT,StockID,cycle);
#
# MarketTradeDayQk(BegT,EndT)
