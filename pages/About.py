import pandas as pd
import streamlit as slt
import datetime
import time
import re
from collections import defaultdict

import pyecharts.options as opts
from pyecharts.charts import Line, HeatMap, Grid, Bar

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


slt.header("这里是！🤔笑笑的表情包研究所！")


EV_DAY_EMOJIS = slt.session_state.emoji_packs
#  = slt.session_state.every_day
slt.write(EV_DAY_EMOJIS[3])
def return_zero():
    return 0


EMOJI_TYPES = defaultdict(return_zero)
EVERY_DAY = slt.session_state.every_day
EVERY_DAY_DETAIL = slt.session_state.every_day_detail



def EMOJI_ANALYSIS():
    
    idxx = 0
    idxx_2 = 0
    quantity_idx_2 = 0
    quantity_idx_1 = 0
    quantity_idx_3 = 0
    for i in EV_DAY_EMOJIS:
        if "productid=\"com.tencent.xin.emoticon.person.stike" in i["Message"]:
            idxx += 1
        if "thumburl = \"http://mmbiz.qpic.cn/" in i["Message"]:
            idxx_2 += 1
        if "type=\"2\"" in i["Message"]:
            quantity_idx_2 += 1
        # elif "type=\"1\"" in i["Message"]:
        #     quantity_idx_1 += 1
        # elif "type=\"3\"" in i["Message"]:
        #     quantity_idx_3 += 1
        if "<gameext type=\"2\"" in i["Message"] and "type=\"2\"" not in i["Message"]:
            quantity_idx_2 -= 1
        # if "<gameext type=\"1\"" in i["Message"] and "type=\"1\"" not in i["Message"]:
        #     quantity_idx_1 -= 1
        # if "<gameext type=\"3\"" in i["Message"] and "type=\"3\"" not in i["Message"]:
        #     quantity_idx_3 -= 1
    
    slt.write("瑜瑜应该还记得我之前一版的聊天记录分析里，对我们使用过的表情包和Emoji进行了简要的分析，这一部分就是一个更加细致的研究！")
    slt.markdown("## 表情包")
    slt.write("一个比较出乎意料，但是仔细想来颇有道理的事实是，完全统计表明，总共", str(len(EV_DAY_EMOJIS)), "条表情包交互中，有",str(quantity_idx_2),"条(", str(round(100 * quantity_idx_2/len(EV_DAY_EMOJIS), 2)), "%)都是动态的表情，静态表情包占比甚至低于",str( round(101 - 100 * quantity_idx_2/len(EV_DAY_EMOJIS), 0)), "%。")
    slt.markdown("> 🧐 看来咱们还是喜欢乱动的可爱小玩意儿")
    slt.write("下面这张图把这些消息拉长到整个", str(len(EVERY_DAY)), "天的时间维度上，看看我们对表情包的喜好如何——")
    slt.markdown("- 和最开始一样，笑笑对数据做了一个滑动平均，每一天的实际表情包发送量取了过去10天之期望，这样把整体趋势更好滴表现出来～")



def get_daily_emoji():
    EMOJI_ANALYSIS()
    emoji_cnts = dict()
    total_msg_cnt = []
    
    for i in EVERY_DAY:
        # print(i)
        total_msg_cnt.append(EVERY_DAY_DETAIL[i][0] + EVERY_DAY_DETAIL[i][1])
        

    for i in EVERY_DAY:
        emoji_cnts[i] = 0
    for i in EV_DAY_EMOJIS:
        cur_day = get_local_time_ymd(i["CreateTime"])[:10]
        cur_emoji = i["Message"]
        EMOJI_TYPES[re.findall('md5=\"(.*?)"', cur_emoji)[0]] += 1    
        emoji_cnts[cur_day] += 1
    
    input_df = pd.DataFrame({"Time" : EVERY_DAY, "EMOJIS": [emoji_cnts[i] for i in EVERY_DAY]})
    input_df["Rolling" ]=  input_df["EMOJIS"].rolling(10).mean()
    input_df["TOTAL_MSG"] = total_msg_cnt
    input_df.index = input_df["Time"]
    # tmp = list(inp)
    c = (
        Bar()

            # init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(
            #     animation_duration=2000, animation_easing="elasticOut"
            # ))
        .add_xaxis(input_df["Time"])
        .add_yaxis("总计的表情包数!",
                input_df["EMOJIS"],
                # is_smooth=True, 
                # symbol = None,
                yaxis_index = 0,
                # linestyle_opts=opts.LineStyleOpts(color='pink'),
                # markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                # markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],  \
                #     label_opts=opts.LabelOpts(is_show=False)),
                
                )
        .add_yaxis("窗口为10天的滑动平均!",
                input_df["Rolling"],
                # is_smooth=True, 
                # symbol = None,
                yaxis_index = 1,
                # linestyle_opts=opts.LineStyleOpts(color='yellow', width = '1'),
                # markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                )
        .extend_axis(
            yaxis=opts.AxisOpts(
                    type_="value",
                    name="总计的表情包数!",
                    min_=0,
                    max_=250,
                    position="right",
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#675bba")
                    ),
                    axislabel_opts=opts.LabelOpts(formatter="{value} 个！"),
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                    # splitline_opts=opts.SplitLineOpts(
                    #     is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    # ),
                )
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                    type_="value",
                    name="表情包数/总聊天数",
                    min_=0,
                    max_=250,
                    position="left",
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#675bba")
                    ),
                    axislabel_opts=opts.LabelOpts(formatter="{value}"),
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                )
        )
        
        # .set_series_opts(
        #     label_opts=opts.LabelOpts(is_show=False),
        # )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            title_opts=opts.TitleOpts(title="表情包数量💝",subtitle="比谁更会发图！",
                                    pos_left=0, pos_top=5),
            # xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(
                name="窗口为10天的滑动平均!",
               
                position="right",
                offset=80,
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} "),
            ),
            # legend_opts = opts.LegendOpts( selected_mode="multiple",pos_left=100,pos_top=80),
        )
    )
    d =  (
        Line()
        .add_xaxis(input_df["Time"])
        .add_yaxis(
            "表情包数/总聊天数",
            # [input_df["EMOJIS"][i] / input_df["TOTAL_MSG"][i] for i in range(len(input_df["EMOJIS"]))],
            input_df["EMOJIS"],
            yaxis_index = 2,
            color="#675bba",
            label_opts=opts.LabelOpts(is_show=False),
        )
    )
    
    d.overlap(c)
    grid = Grid()
    grid.add(d, opts.GridOpts(pos_left="5%", pos_right="20%"), is_control_axis_index=True)
    

    st_pyecharts(grid)
    return input_df
    
INPUT_DF = get_daily_emoji()

def TimeSeries_analysis():
    temp_ipt = INPUT_DF
    temp_ipt.index = [(i+ 1) for i in range(len(EVERY_DAY))]
    
    del temp_ipt["Time"]
    del temp_ipt["Rolling"]
    print(temp_ipt)
    test = adf(temp_ipt, autolag="AIC")
    
    print("P-value = {}".format(test[1]) )
    

def test():
    x_data = ["{}月".format(i) for i in range(1, 13)]
    bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis(
            "蒸发量",
            [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3],
            yaxis_index=0,
            color="#d14a61",
        )
        .add_yaxis(
            "降水量",
            [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3],
            yaxis_index=1,
            color="#5793f3",
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="蒸发量",
                type_="value",
                min_=0,
                max_=250,
                position="right",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#d14a61")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} ml"),
            )
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                name="温度",
                min_=0,
                max_=25,
                position="left",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#675bba")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} °C"),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                ),
            )
        )
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                name="降水量",
                min_=0,
                max_=250,
                position="right",
                offset=80,
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} ml"),
            ),
            title_opts=opts.TitleOpts(title="Grid-多 Y 轴示例"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        )
    )

    line = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis(
            "平均温度",
            [2.0, 2.2, 3.3, 4.5, 6.3, 10.2, 20.3, 23.4, 23.0, 16.5, 12.0, 6.2],
            yaxis_index=2,
            color="#675bba",
            label_opts=opts.LabelOpts(is_show=False),
        )
    )

    bar.overlap(line)
    grid = Grid()
    grid.add(bar, opts.GridOpts(pos_left="5%", pos_right="20%"), is_control_axis_index=True)
    st_pyecharts(grid)

test()
    # print(idxx)

    # print(idxx_2)

    # print(quantity_idx_1)

    # print(quantity_idx_2)

    # print(quantity_idx_3)
# slt.write(EV_DAY_EMOJIS[1])