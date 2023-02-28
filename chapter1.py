import streamlit as slt
import datetime
import json
import time
import pandas as pd
import numpy as np
from collections import defaultdict
import pyecharts.options as opts
from pyecharts.charts import Line, HeatMap, Grid, Bar
import random
from streamlit_echarts import st_pyecharts
import os
import sqlite3

os.environ['TZ'] = 'Asia/Shanghai'

slt.set_page_config(
    page_title="奇奇怪怪的发电中心站",   
    page_icon="🦈",  
    layout="wide",
    initial_sidebar_state="expanded",  
)

if 'first_visit' not in slt.session_state:
    slt.session_state.first_visit=True
else:
    slt.session_state.first_visit=False
if slt.session_state.first_visit:
    slt.balloons()  #第一次访问时才会放气球


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



def get_local_timestamp(date_time):
    """ 返回本地时间的时间戳格式

    Args:
        date_time (_type_): _description_

    Returns:
        _type_: _description_
    """
    timeArray = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timeArray.timetuple()))


# @slt.experimental_memo # experimental_memo 这个处理缓存效果比cache要好得多
# @slt.experimental_singleton
# 
@slt.experimental_memo
def load_data(address):
    temp = ""
    max_msg_vol = 0
    max_msg_date = 0
    hours_msgs = [0 for _ in range(24)] # 16w消息分布在哪些小时中
    weekday_msgs = [0 for _ in range(7)] # 16w消息分布在星期几

    messenger = defaultdict(def_value) # 消息总数
    types = defaultdict(def_value_list) # 消息的种类：按照分类进行排布
    
    CONN = sqlite3.connect('./static/files/chathistory.db')
    cursor = CONN.cursor()
    execute_sentence = "select createTime, Des, Message, Type from chathistory"
    temp =  cursor.execute(execute_sentence).fetchall()
    cursor.close()
    CONN.close()

    left = temp[0][0] # 开始时间（精确到秒）
    right = temp[-1][0] # 结束时间(精确到秒)

    left_day_ymd = get_local_time_ymd(left)[:10] # 获取第一天的 "%y-%m-%d" string，结果是YYYY-MM-DD
    right_day_ymd = get_local_time_ymd(right)[:10] # 获取最后一天的 "%y-%m-%d" string

    every_day = list(pd.date_range(left_day_ymd, right_day_ymd, freq = "D")) # 每一天的string格式 "%y-%m-%d"

    every_day_timestamp = [get_local_timestamp(str(i)) for i in every_day] # 每一天的timestamp(Integer)格式
    # 调整every_day格式，保留ymd

    for i in range(len(every_day)):
        every_day[i] = str(every_day[i])[:10]

    every_day_detail = dict()
    every_day_detail[every_day[0]] = defaultdict(def_value_list)

    tail = defaultdict(def_value_list)
    start_idx = 0
    tmp_idx = 0

    week_day_cnt = [[i, j , 0] for i in range(24) for j in range(7) ] # 统计消息的数量

    emoji_packs = []

    for idx, i in enumerate(temp): # 统计消息数量
        messenger[i[1]] += 1
        types[i[3]][i[1]] += 1
        if start_idx + 1 < len(every_day_timestamp) and i[0] < every_day_timestamp[start_idx + 1]:
            every_day_detail[every_day[start_idx]][i[3]][i[1]] += 1
        elif start_idx + 1 < len(every_day_timestamp) and i[0] >= every_day_timestamp[start_idx + 1]:
            if max_msg_vol < (idx - tmp_idx):
                max_msg_date = every_day[start_idx]
                max_msg_vol = idx - tmp_idx
            tmp_idx = idx
            start_idx += 1
            every_day_detail[every_day[start_idx]] = defaultdict(def_value_list)
            every_day_detail[every_day[start_idx]][i[3]][i[1]] += 1
        else:
            if len(temp) - idx > max_msg_vol:
                max_msg_vol = len(temp) - idx
                max_msg_date = every_day[-1]
            tail[i[3]][i[1]] += 1

        if i[3] == 47:
            emoji_packs.append(i)
        
        tmp_wk_detail = datetime.datetime.fromtimestamp(i[0])
        wk_day = tmp_wk_detail.weekday()
        wk_hour = int(tmp_wk_detail.hour)
        week_day_cnt[wk_hour * 7 + wk_day][2] += 1
        hours_msgs[wk_hour] += 1 
        weekday_msgs[wk_day] += 1

# "select createTime, Des, Message, Type from chathistory"
    every_day_detail[every_day[-1]] = tail

    return temp, messenger, left, right, types, every_day, every_day_timestamp, \
        every_day_detail, max_msg_date, max_msg_vol, week_day_cnt, emoji_packs, hours_msgs, weekday_msgs

def def_value():
    return 0
def def_value_list():
    return [0, 0]

ADDRESS = "./chathistory.json"
CHAT_HISTORY, TOTAL_CNT, START_TIMESTAMP, END_TIMESTAMP, TYPES_CNT, EVERY_DAY, \
    EVERY_DAY_TIMESTAMP, EVERY_DAY_DETAIL, MAX_MSG_DATE , MAX_MSG_VOL, WEEK_DAY_CNT, EMOJI_PACKS, \
        HOURS_MSGS, WEEKDAY_MSGS = load_data(ADDRESS)

def TYPES_CNT_process():

    # 10002 ： 撤回消息
    # 1: 普通消息
    # 47: 表情包
    # 3: 图片
    # 49：回复某些msg/分享的外链接等
    # 50: vx通话情况
    # 43: 视频消息
    # 10000: 红包/拍一拍/撤回等系统消息
    # 48：定位分享
    # 34：语音
    # 42：
    msg_idx = [1, 47, 49, 10000, 10002, 3, 34, 43, 50, 48, 42 ]
    msg_del = [TYPES_CNT[i][0] for i in msg_idx]
    tmp = sum(msg_del[2:5])
    msg_del = msg_del[:2] + msg_del[5:]
    msg_del.append(tmp)
    msg_rec = [TYPES_CNT[i][1] for i in msg_idx]
    tmp = sum(msg_rec[2:5])
    msg_rec = (msg_rec[:2] + msg_rec[5:])
    msg_rec.append(tmp)
    TYPES_CNT_dataframe = pd.DataFrame({ "消息类型":["文字消息", "表情包", "图片消息", "语音消息", \
        "视频消息", "VX通话", "定位分享", "联系人推荐", "消息引用｜外链分享｜拍一拍｜撤回"], "瑜瑜子的": np.array(msg_rec),\
             "笑笑子的": np.array(msg_del), "总计": np.array(msg_del) + np.array(msg_rec), "占总消息比%": \
                np.around((np.array(msg_del) + np.array(msg_rec)) * 100 / len(CHAT_HISTORY) , 3) })
    # TYPES_CNT_dataframe.set_index("消息类型")
    return TYPES_CNT_dataframe
    
TOTAL_MSG = len(CHAT_HISTORY)
slt.session_state.load_data = CHAT_HISTORY
slt.session_state.emoji_packs = EMOJI_PACKS
slt.session_state.every_day = EVERY_DAY
slt.session_state.every_day_detail = EVERY_DAY_DETAIL

# 利用页面缓存减少冲突

slt.markdown("# 奇奇怪怪的聊天站")
slt.caption("🧐 什么聊天站！进来看看！")


def get_msg_vol(timestamp1, timestamp2):
    start = 0
    end = TOTAL_MSG - 1
    indx1 = -1
    indx2 = -1
    while start <= end:
        mid = start + ((end - start) >> 1)
        if CHAT_HISTORY[mid][0] > timestamp1:
            indx1 = mid
            end = mid - 1
        else:
            start = mid + 1
    start = 0
    end = TOTAL_MSG - 1
    while start <= end:
        mid = start + ((end - start) >> 1)
        if CHAT_HISTORY[mid][0] > timestamp2:
            indx2 = mid
            end = mid - 1
        else:
            start = mid + 1
    return int(abs(indx1 - indx2)), indx1, indx2


def get_interval_time(timestamp1, timestamp2):
    result = (timestamp2 - timestamp1) // 60 // 60 // 24
    return result

def get_local_time(timeStamp):
    """ 从时间戳获取当地时间

    Args:
        timeStamp (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    t  = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", t.timetuple())
    return otherStyleTime

def show_profile():
    days = get_interval_time(START_TIMESTAMP, END_TIMESTAMP)
    slt.write("总共有", str(TOTAL_MSG) ,"条消息, 最早的消息来自瑜瑜子，发送时间是", \
        get_local_time(START_TIMESTAMP), "而最晚的消息是笑笑在", get_local_time(END_TIMESTAMP) , \
            "发送的。", "在这", str(days), "天中，我们畅所欲言，无话不谈。\
                平均每天要唠唠叨叨",  str(TOTAL_MSG // days  ), "条。")
    slt.write("记录显示，在", MAX_MSG_DATE, "这一天，我们是两只大话痨，一共发送了", str(MAX_MSG_VOL), "条消息，是有史以来最多的一天，\
        这意味着那24个小时里，我们每隔1分钟就发1条消息，整天不休。" )
    slt.write("2022-08-02 这个日子也比较独特。瑜瑜和笑笑\
        怒刷了1428条微信记录，那天打开了话匣子的瑜瑜发送了626条消息。炎炎夏日挡不住恋人的絮絮叨叨💑。")

show_profile()

def show_sidebar():
    slt.sidebar.header("一些小玩具🧸!")
    d = slt.sidebar.date_input(
        "🛩️  聊天记录查询站｜选个日子！ :kiss:",
        datetime.date(2022, 1, 1))
    slt.sidebar.write('你选择的日期 📅 是:', d)
    ans, idx1, idx2 = get_msg_vol(get_local_timestamp(str(d) + " 00:00:00"), \
        get_local_timestamp(str(d) + " 23:59:59"))
    slt.sidebar.write("Msg volume for the selected day " , d, " is ", str(ans))
    slt.sidebar.write("这一天， \n \n瑜瑜发了{}条文字，甩了{}条表情包\
        ；\n \n 笑笑发了{}条文字，甩了{}个表情包".format(str(EVERY_DAY_DETAIL[str(d)][1][1]), EVERY_DAY_DETAIL[str(d)][47][1], EVERY_DAY_DETAIL[str(d)][1][0], EVERY_DAY_DETAIL[str(d)][47][0]))
    slt.sidebar.markdown("------")

   
show_sidebar()

def show_types_cnt():
    TYPES_CNT_dataframe = TYPES_CNT_process()
    hide_table_row_index = """
                <style>
                thead {display:none};
                tbody th {text-align: center; background : #112233};
                </style>
                """
    slt.markdown(hide_table_row_index, unsafe_allow_html=True)
    slt.table(TYPES_CNT_dataframe.T)
    slt.info("解释一下为什么⬆️表最后一列如此突兀：原本这部分的每条信息是分成3种不同的Type（10000，10002，49）显示在json文件中，\
    但是仔细梳理会发现其中的\"撤回\"，一部分是10000类，一部分是10002类，甚至有一部分属于49类，最奇葩的是上述三种类中都包含了笑笑的撤回、瑜瑜的撤回，使得统计各自\
        撤回数量成为一件十分低效繁琐的事情，综合考虑运行效率，就把这三种的数据全部合在了一起。 ")

show_types_cnt()

def show_marco_line_graph():
    """
        绘制宏观的聊天记录数量折线图
    """
    input_data = [[0 for _ in range(len(EVERY_DAY))] for _ in range(4)]
    for day, i in enumerate(EVERY_DAY):
        cur_dict = EVERY_DAY_DETAIL[i]
        for j in cur_dict:
            input_data[0][day] += cur_dict[j][0]
            input_data[1][day] += cur_dict[j][1]
        input_data[2][day] = input_data[0][day] + input_data[1][day]
        input_data[3][day] = input_data[1][day] - input_data[0][day]

    c = (
        Line(init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(
                animation_duration=2000, animation_easing="elasticOut"
            )))
        .add_xaxis(EVERY_DAY)
        .add_yaxis("天瑜的!",
                input_data[1], 
                is_smooth=True, 
                symbol = None,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],  \
                    label_opts=opts.LabelOpts(is_show=False)),
                areastyle_opts=opts.AreaStyleOpts(opacity=0.2, color="rgba(245,212,217,0.15)"),
                )
        .add_yaxis("笑笑的!", 
                input_data[0], 
                is_smooth=True, 
                symbol = None,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],  \
                    label_opts=opts.LabelOpts(is_show=False)))
        .add_yaxis("一起的!", 
                input_data[2],
                is_smooth=True,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")] ),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],  \

                    label_opts=opts.LabelOpts(is_show=False)))
                
        .add_yaxis("差!", 
                input_data[3],
                is_smooth=True,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")] ),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],  \
                    label_opts=opts.LabelOpts(is_show=False)))
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            # markline_opts=opts.MarkLineOpts(data = [opts.MarkLineItem(xco ord = "2022-01-01")])  
            
        )
        .set_global_opts(
            # toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            title_opts=opts.TitleOpts(title="对话数量",subtitle="WeChat骚话大赏!",
                                    pos_left=0, pos_top=5),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            legend_opts = opts.LegendOpts( selected_mode="multiple",pos_left=100,pos_top=80),
        )
    )
    st_pyecharts(c, height="650px")
    return input_data

MACRO_DATA = show_marco_line_graph()

def show_rolling_window():
    temp_pd = pd.DataFrame({"She": MACRO_DATA[2], "Time": EVERY_DAY })
    temp_pd.set_index = "Time"
    temp_pd['She'] = temp_pd['She'].rolling(10).mean()
    a = (
        Line(init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(
                animation_duration=2000, animation_easing="elasticOut"
            )))
        .add_xaxis(EVERY_DAY)
        .add_yaxis("10天的滑动平均!",
                temp_pd["She"], 
                is_smooth=True, 
                symbol = None,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")], label_opts=opts.LabelOpts(is_show=False)),
                areastyle_opts=opts.AreaStyleOpts(opacity=0.2, color="rgba(245,212,217,0.15)"),     
        )
        .set_series_opts(
            markarea_opts=opts.MarkAreaOpts(
                data=[
                    opts.MarkAreaItem(name="上学🎒", x=("2021-10-08", "2022-01-13")
                                    ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(245,212,217,0.15)')),
                    opts.MarkAreaItem(name="放寒假🥳", x=("2022-01-13", "2022-02-12")
                                    ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(241,158,194,0.25)')),
                    opts.MarkAreaItem(name="上学🎒", x=("2022-02-12", "2022-06-25")
                                    ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(245,212,217,0.15)')),
                                    # color =
                    opts.MarkAreaItem(name="放暑假🥰", x=("2022-06-25", "2022-08-17")
                                    ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(241,158,194,0.25)')),
                    opts.MarkAreaItem(name="上学🎒", x=("2022-08-17", "2022-10-04")
                                    ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(245,212,217,0.15)')),
                ]
            ),
        )
    
        .set_global_opts(
            
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            title_opts=opts.TitleOpts(title="对话总量的滑动平均(MA)",subtitle="WeChat骚话大赏!",
                                    pos_left=0, pos_top=5),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            legend_opts = opts.LegendOpts( selected_mode="multiple",pos_left=100,pos_top=80),
            # = opts.AnimationOpts(animation_duration = 2000)
        )  
    )


    st_pyecharts(a, height="450px")
show_rolling_window()


def show_heat_graph():
    average_per_day = len(CHAT_HISTORY) // (24 * 7)
    record_max = record_min = 0
    for i in range(len(WEEK_DAY_CNT)):
        
        WEEK_DAY_CNT[i][2] -= average_per_day
        if record_max < WEEK_DAY_CNT[i][2]:
            record_max = WEEK_DAY_CNT[i][2]
        if record_min > WEEK_DAY_CNT[i][2]:
            record_min = WEEK_DAY_CNT[i][2]
    
    # for i in range(len(WEEK_DAY_CNT)):
    #     if WEEK_DAY_CNT[i][2] >= 0:
    #         WEEK_DAY_CNT[i][2] = (100 * WEEK_DAY_CNT[i][2])/record_max
    #     if WEEK_DAY_CNT[i][2] < 0:
    #         WEEK_DAY_CNT[i][2] =(-100 * WEEK_DAY_CNT[i][2])/record_min

    c = (
        HeatMap(init_opts=opts.InitOpts(height="600px"))
        .add_xaxis([str(i) for i in range(24)])
        .add_yaxis(
            "",
            ["周一","周二","周三","周四","周五","周六","周日"],
            WEEK_DAY_CNT,
            label_opts=opts.LabelOpts(is_show=True, position="inside"),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="item", axis_pointer_type="cross"),
            title_opts=opts.TitleOpts(title="星期-时间热力图"),
            visualmap_opts=opts.VisualMapOpts(\
                min_ = record_min - 1, max_  = record_max + 1, is_calculable=True, orient="horizontal", \
                    pos_left="center", type_="color", range_opacity=0.9, precision = 0, dimension=2),
        )
    )
    bar_ = (
        Bar(init_opts=opts.InitOpts(height="600px"))
        .add_xaxis(["周一","周二","周三","周四","周五","周六","周日"])
        .add_yaxis("消息数量", WEEKDAY_MSGS, color = "#5793f3")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="星期分布"),
            
        )
    )
    bar2 = (
        Bar(init_opts=opts.InitOpts(height="600px"))
        .add_xaxis(["{}时".format(i) for i in range(24)])
        .add_yaxis("消息数量", HOURS_MSGS,color = "#d14a61",\
            markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")] , label_opts=opts.LabelOpts(is_show=False)))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="时间分布", pos_bottom="50%"),
            brush_opts=opts.BrushOpts(),
        )
    )

    grid = Grid(init_opts=opts.InitOpts(width = "700px", height = "1200px"))
    grid.add(bar_, grid_opts=opts.GridOpts(pos_bottom="55%"))
    grid.add(bar2, grid_opts=opts.GridOpts(pos_top="55%"))

    st_pyecharts(c)
    st_pyecharts(grid, height = "550px")
    
show_heat_graph()
# slt.write(EMOJI_PACKS)

# slt.write(len(EMOJI_PACKS))
    
# slt.write([[i, TYPES_CNT[i][0], TYPES_CNT[i][1]] for i in TYPES_CNT])
# slt.write([str(i)[:10] for i in DAYS])
# slt.write(DAYS[0] > "212842")
# slt.write(EVERY_DAY_DETAIL)



# slt.markdown("""| 信息格式  | `笑笑`发的！ |  `瑜瑜`发的！ | 
# | :-------------: | :----------: | ------------: |
# | hhhhh |   centered   | right-aligned |
# |      |    中对齐     |         右对齐 | """)
# 10002 ： 撤回消息
# 1: 普通消息
# 47: 表情包
# 3: 图片
# 49：回复某些msg/分享的外链接等
# 50: vx通话情况
# 43: 视频消息
# 10000: 红包/拍一拍/撤回等系统消息
# 48：定位分享
# 34：语音
# 42：
