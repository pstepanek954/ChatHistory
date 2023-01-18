import pandas as pd
import streamlit as slt
import datetime
import time
import re
from collections import defaultdict


import pyecharts.options as opts
from pyecharts.charts import Line, HeatMap
import random
from streamlit_echarts import st_pyecharts
import os

import math
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller as adf 
from statsmodels.stats.diagnostic import acorr_ljungbox as lbtest
from statsmodels.tsa.arima.model import ARIMA



os.environ['TZ'] = 'Asia/Shanghai'


def get_local_time_ymd(timeStamp):

    """ 从时间戳获取当地时间
     仅仅返回年月日：Year Month Day

    Args:
        timeStamp (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    t = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d", t.timetuple() )
    return otherStyleTime


slt.header("这里是！🤔表情包研究所！")


EV_DAY_EMOJIS = slt.session_state.emoji_packs
#  = slt.session_state.every_day
slt.write(EV_DAY_EMOJIS[3])
def return_zero():
    return 0


EMOJI_TYPES = defaultdict(return_zero)
EVERY_DAY = slt.session_state.every_day



def get_daily_emoji():
    emoji_cnts = dict()
    for i in EVERY_DAY:
        emoji_cnts[i] = 0
    for i in EV_DAY_EMOJIS:
        cur_day = get_local_time_ymd(i["CreateTime"])[:10]
        cur_emoji = i["Message"]
        EMOJI_TYPES[re.findall('md5=\"(.*?)"', cur_emoji)[0]] += 1    
        emoji_cnts[cur_day] += 1
    
    input_df = pd.DataFrame({"Time" : EVERY_DAY, "EMOJIS": [emoji_cnts[i] for i in EVERY_DAY]})
    input_df["Rolling" ]=  input_df["EMOJIS"].rolling(10).mean()
    input_df.index = input_df["Time"]
    c = (
        Line(init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(
                animation_duration=2000, animation_easing="elasticOut"
            )))
        .add_xaxis(input_df["Time"])
        .add_yaxis("总计的表情包数!",
                input_df["EMOJIS"],
                is_smooth=True, 
                symbol = None,
                linestyle_opts=opts.LineStyleOpts(color='pink'),
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],  \
                    label_opts=opts.LabelOpts(is_show=False)),
                
                )
        .add_yaxis("窗口为10天的滑动平均!",
                input_df["Rolling"],
                is_smooth=True, 
                symbol = None,
                linestyle_opts=opts.LineStyleOpts(color='yellow', width = '1'),
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            title_opts=opts.TitleOpts(title="表情包数量💝",subtitle="比谁更会发图！",
                                    pos_left=0, pos_top=5),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            legend_opts = opts.LegendOpts( selected_mode="multiple",pos_left=100,pos_top=80),
        )
    )
    st_pyecharts(c)
    return input_df

INPUT_DF = get_daily_emoji()


def TimeSeries_analysis():
    temp_ipt = INPUT_DF
    temp_ipt.index = [(i+ 1) for i in range(len(EVERY_DAY))]
    # INPUT_DF.index = INPUT_DF["Time"]
    del temp_ipt["Time"]
    del temp_ipt["Rolling"]
    print(temp_ipt)
    
    # t = plt.figure(figsize=(2,1))
    # t = plot_acf(temp_ipt, lags=10)
    # t = plt.figure(figsize=(3,2))

    test = adf(temp_ipt, autolag="AIC")
    
    print("P-value = {}".format(test[1]) )
    
    # slt.pyplot(t)
    
    
# TimeSeries_analysis()










# slt.write(len(a))
# slt.write(a[21])
# for i in 


