import streamlit as slt
import datetime
import json
import time
import pandas as pd
import numpy as np
from collections import defaultdict
import pyecharts.options as opts
from pyecharts.charts import Line, HeatMap, Grid, Bar, Bar3D
import random
from streamlit_echarts import st_pyecharts
import os
import sqlite3

os.environ['TZ'] = 'Asia/Shanghai'



if 'first_visit' not in slt.session_state:
    slt.session_state.first_visit = True
else:
    slt.session_state.first_visit = False
if slt.session_state.first_visit:
    slt.balloons()  # 第一次访问时才会放气球


def get_local_time_ymd(timeStamp):
    """ 从时间戳获取当地时间
     仅仅返回年月日：Year Month Day

    Args:
        timeStamp (_type_): _description_

    Returns:
        _type_: _description_
    """

    t = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d", t.timetuple())
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

@slt.experimental_memo
def load_data(address):
    temp = ""
    max_msg_vol = 0
    max_msg_date = 0
    hours_msgs = [0 for _ in range(24)]  # 16w消息分布在哪些小时中
    weekday_msgs = [0 for _ in range(7)]  # 16w消息分布在星期几

    messenger = defaultdict(def_value)  # 消息总数
    types = defaultdict(def_value_list)  # 消息的种类：按照分类进行排布

    CONN = sqlite3.connect('./static/files/20230327.db')
    cursor = CONN.cursor()
    execute_sentence = "select createTime, Des, Message, Type from chathistory"
    temp = cursor.execute(execute_sentence).fetchall()
    cursor.close()
    CONN.close()

    left = temp[0][0]  # 开始时间（精确到秒）
    right = temp[-1][0]  # 结束时间(精确到秒)

    # 获取第一天的 "%y-%m-%d" string，结果是YYYY-MM-DD
    left_day_ymd = get_local_time_ymd(left)[:10]
    right_day_ymd = get_local_time_ymd(right)[:10]  # 获取最后一天的 "%y-%m-%d" string

    # 每一天的string格式 "%y-%m-%d"
    every_day = list(pd.date_range(left_day_ymd, right_day_ymd, freq="D"))

    every_day_timestamp = [get_local_timestamp(
        str(i)) for i in every_day]  # 每一天的timestamp(Integer)格式
    # 调整every_day格式，保留ymd

    for i in range(len(every_day)):
        every_day[i] = str(every_day[i])[:10]

    every_day_detail = dict()
    every_day_detail[every_day[0]] = defaultdict(def_value_list)

    tail = defaultdict(def_value_list)
    start_idx = 0
    tmp_idx = 0

    week_day_cnt = [[i, j, 0] for i in range(24) for j in range(7)]  # 统计消息的数量

    emoji_packs = []

    talks_contents = []

    for idx, i in enumerate(temp):  # 统计消息数量
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
            every_day_detail[every_day[start_idx]
                             ] = defaultdict(def_value_list)
            every_day_detail[every_day[start_idx]][i[3]][i[1]] += 1
        else:
            if len(temp) - idx > max_msg_vol:
                max_msg_vol = len(temp) - idx
                max_msg_date = every_day[-1]
            tail[i[3]][i[1]] += 1

        if i[3] == 47:
            emoji_packs.append(i)
        elif i[3] == 1:
            talks_contents.append([i[2], i[0]])

        tmp_wk_detail = datetime.datetime.fromtimestamp(i[0])
        wk_day = tmp_wk_detail.weekday()
        wk_hour = int(tmp_wk_detail.hour)
        week_day_cnt[wk_hour * 7 + wk_day][2] += 1
        hours_msgs[wk_hour] += 1
        weekday_msgs[wk_day] += 1

# "select createTime, Des, Message, Type from chathistory"
    every_day_detail[every_day[-1]] = tail

    return temp, messenger, left, right, types, every_day, every_day_timestamp, \
        every_day_detail, max_msg_date, max_msg_vol, week_day_cnt, emoji_packs, hours_msgs, weekday_msgs, talks_contents


def def_value():
    return 0


def def_value_list():
    return [0, 0]


ADDRESS = "./chathistory.json"
CHAT_HISTORY, TOTAL_CNT, START_TIMESTAMP, END_TIMESTAMP, TYPES_CNT, EVERY_DAY, \
    EVERY_DAY_TIMESTAMP, EVERY_DAY_DETAIL, MAX_MSG_DATE, MAX_MSG_VOL, WEEK_DAY_CNT, EMOJI_PACKS, \
    HOURS_MSGS, WEEKDAY_MSGS, TALKS_CONTENTS = load_data(ADDRESS)


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
    msg_idx = [1, 47, 49, 10000, 10002, 3, 34, 43, 50, 48, 42]
    msg_del = [TYPES_CNT[i][0] for i in msg_idx]
    tmp = sum(msg_del[2:5])
    msg_del = msg_del[:2] + msg_del[5:]
    msg_del.append(tmp)
    msg_rec = [TYPES_CNT[i][1] for i in msg_idx]
    tmp = sum(msg_rec[2:5])
    msg_rec = (msg_rec[:2] + msg_rec[5:])
    msg_rec.append(tmp)
    TYPES_CNT_dataframe = pd.DataFrame({"消息类型": ["文字消息", "表情包", "图片消息", "语音消息",
                                                 "视频消息", "VX通话", "定位分享", "联系人推荐", "消息引用｜外链分享｜拍一拍｜撤回"], "瑜瑜子的": np.array(msg_rec),
                                        "笑笑子的": np.array(msg_del), "总计": np.array(msg_del) + np.array(msg_rec), "占总消息比%":
                                        np.around((np.array(msg_del) + np.array(msg_rec)) * 100 / len(CHAT_HISTORY), 3)})
    # TYPES_CNT_dataframe.set_index("消息类型")
    return TYPES_CNT_dataframe


TOTAL_MSG = len(CHAT_HISTORY)
slt.session_state.load_data = CHAT_HISTORY
slt.session_state.emoji_packs = EMOJI_PACKS
slt.session_state.every_day = EVERY_DAY
slt.session_state.every_day_detail = EVERY_DAY_DETAIL
slt.session_state.talks_contents = TALKS_CONTENTS

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

    t = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", t.timetuple())
    return otherStyleTime


def show_profile():
    days = get_interval_time(START_TIMESTAMP, END_TIMESTAMP)
    slt.markdown("-------------")
    slt.markdown("### 概述")
    slt.write("&ensp;&ensp;&ensp;&ensp;将所有的记录信息导出之后，完全统计显示，到", get_local_time(
        END_TIMESTAMP), "，笑笑发出最后一条消息为止，瑜瑜和笑笑一共发送了", str(TOTAL_MSG), "条消息, 最早的消息来自瑜瑜子，发送时间是",
        get_local_time(START_TIMESTAMP), "。在这", str(days), "天中，我们畅所欲言，无话不谈。\
                平均每天要唠唠叨叨",  str(TOTAL_MSG // days), "条。")
    slt.caption("&ensp;&ensp;&ensp;&ensp;有说不尽的话，也有吐不完的槽。")
    slt.write("&ensp;&ensp;&ensp;&ensp;如果瑜瑜还记得", MAX_MSG_DATE, "这一天。那天我们是两只大话痨，一共发送了", str(MAX_MSG_VOL), "条消息，是所有日子里最多的。\
        这意味着那24个小时里，我们平均每隔1分钟就会发送1条消息，整天不休。")
    slt.write("&ensp;&ensp;&ensp;&ensp;2022-08-02 这个日子也比较独特。瑜瑜和笑笑一共传递了1428条微信消息，那天瑜瑜很兴奋，打开了话匣子的你发送了626条消息，炎炎夏日挡不住恋人的絮絮叨叨💑。")
    slt.caption(
        "&ensp;&ensp;&ensp;&ensp;对了那一天一架来自美国的飞机降落在了台湾岛，不知道我们是在聊国际大事还是聊生活琐屑呢～")
    slt.write("&ensp;&ensp;&ensp;&ensp;笑笑借助微信给每条信息的标注，将这23万条数据进行了简单的分类，统计如下表所示。说实话当我第一次看到这张表的时候，内心还是有些震撼的。有人质疑冷冰冰的\"量化\"有什么意义。\
              实际上这种质疑是有道理的。除非——当你看着这一行行数字，然后有人默默地告诉你，我们相遇以来、过去一年多之中，无论你是喜是悲，是考试前的自我怀疑、通宵复习，还是做出成果的欣喜若狂、喜笑颜开，是我们之间快乐的时刻，还是小有矛盾的不快，所有种种情绪、脾气、心事，都默默地躺在这23万条数据之中\
              。它们无言，但一直在见证。而见证，就是最终的意义。我触摸不了时间，但是当时间通过数据向我伸出手，我会紧紧握住。")


show_profile()


def show_sidebar():
    slt.sidebar.header("一些小玩具🧸!")
    d = slt.sidebar.date_input(
        "🛩️  聊天记录查询站｜选个日子！ :kiss:",
        datetime.date(2022, 1, 1))
    slt.sidebar.write('你选择的日期 📅 是:', d)
    ans, idx1, idx2 = get_msg_vol(get_local_timestamp(str(d) + " 00:00:00"),
                                  get_local_timestamp(str(d) + " 23:59:59"))
    slt.sidebar.write("这一天， ", d, " 的微信聊天记录有 ", str(ans), " 条；")
    slt.sidebar.write("这一天， \n \n瑜瑜发了{}条文字，甩了{}条表情包\
        ；\n \n 笑笑发了{}条文字，甩了{}个表情包；".format(str(EVERY_DAY_DETAIL[str(d)][1][1]), EVERY_DAY_DETAIL[str(d)][47][1], EVERY_DAY_DETAIL[str(d)][1][0], EVERY_DAY_DETAIL[str(d)][47][0]))
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
    slt.info("&ensp;&ensp;&ensp;&ensp; 🤖️ 简单解释一下为什么⬆️表最后一列如此突兀：原本这部分的每条信息是分成3种不同的Type（10000，10002，49）显示在json文件中，\
    但是仔细梳理后发现其中的\"撤回\"，一部分属于10000类，一部分属于10002类，甚至有一部分属于49类，最奇葩的是上述三种类中都包含了笑笑的撤回、瑜瑜的撤回，这使得统计各自\
撤回数量成为一件十分低效繁琐且很难核实准确性的事情，综合考虑运行效率，就把这三种的数据全部合在了一起。 ")


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
    bar_1 = (
        Bar()
        .add_xaxis(EVERY_DAY)
        .add_yaxis("天瑜的！", input_data[1], stack="stack1", category_gap=0,
                   itemstyle_opts=opts.ItemStyleOpts(color="#ffb4ac"),
                   markpoint_opts=opts.MarkPointOpts(
                       data=[opts.MarkPointItem(type_="max")]))
        .add_yaxis("笑笑的！", input_data[0], stack="stack1", category_gap=0,
                   itemstyle_opts=opts.ItemStyleOpts(color="#679186"),
                   markpoint_opts=opts.MarkPointOpts(
                       data=[opts.MarkPointItem(type_="max")]))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="聊天全记录", subtitle="WeChat骚话大赏!", pos_left=0, pos_top=5),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),

            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(type_="value",
                                     axistick_opts=opts.AxisTickOpts(
                                         is_show=True),
                                     splitline_opts=opts.SplitLineOpts(
                                         is_show=True),
                                     axislabel_opts=opts.LabelOpts(
                                         formatter="{value} 条")
                                     ),
            legend_opts=opts.LegendOpts(
                selected_mode="multiple", pos_left=100, pos_top=80),
            datazoom_opts=[
                opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            brush_opts=opts.BrushOpts(),
        )
        # .render("bar_stack0.html")
    )
    st_pyecharts(bar_1, height="500px")
    # c = (
    #     Line(init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(
    #         animation_duration=2000, animation_easing="elasticOut"
    #     )))
    #     .add_xaxis(EVERY_DAY)
    #     .add_yaxis("天瑜的!",
    #                input_data[1],
    #                is_smooth=True,
    #                symbol=None,
    #                markpoint_opts=opts.MarkPointOpts(
    #                    data=[opts.MarkPointItem(type_="max")]),
    #                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],
    #                                                label_opts=opts.LabelOpts(is_show=False)),
    #                areastyle_opts=opts.AreaStyleOpts(
    #                    opacity=0.2, color="rgba(245,212,217,0.15)"),
    #                )
    #     .add_yaxis("笑笑的!",
    #                input_data[0],
    #                is_smooth=True,
    #                symbol=None,
    #                markpoint_opts=opts.MarkPointOpts(
    #                    data=[opts.MarkPointItem(type_="max")]),
    #                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],
    #                                                label_opts=opts.LabelOpts(is_show=False)))
    #     .add_yaxis("一起的!",
    #                input_data[2],
    #                is_smooth=True,
    #                markpoint_opts=opts.MarkPointOpts(
    #                    data=[opts.MarkPointItem(type_="max")]),
    #                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],

    #                                                label_opts=opts.LabelOpts(is_show=False)))

    #     .add_yaxis("差!",
    #                input_data[3],
    #                is_smooth=True,
    #                markpoint_opts=opts.MarkPointOpts(
    #                    data=[opts.MarkPointItem(type_="max")]),
    #                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],
    #                                                label_opts=opts.LabelOpts(is_show=False)))
    #     .set_series_opts(
    #         label_opts=opts.LabelOpts(is_show=False),
    #         # markline_opts=opts.MarkLineOpts(data = [opts.MarkLineItem(xco ord = "2022-01-01")])

    #     )
    #     .set_global_opts(
    #         # toolbox_opts=opts.ToolboxOpts(),
    #         tooltip_opts=opts.TooltipOpts(
    #             trigger="axis", axis_pointer_type="cross"),
    #         title_opts=opts.TitleOpts(title="对话数量", subtitle="WeChat骚话大赏!",
    #                                   pos_left=0, pos_top=5),
    #         xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
    #         legend_opts=opts.LegendOpts(
    #             selected_mode="multiple", pos_left=100, pos_top=80),
    #         datazoom_opts=[opts.DataZoomOpts()],
    #     )
    # )
    # st_pyecharts(c, height="650px")
    return input_data


MACRO_DATA = show_marco_line_graph()


def show_rolling_window():
    slt.markdown(
        "&ensp;&ensp;&ensp;&ensp;上面的可交互图表提供了我们一年半以来每天的聊天记录的情况。总体来看笑笑的话痨程度丝毫没有减少，分别出现了两次峰值；相比之下瑜瑜的信息更加平稳。")
    slt.markdown("&ensp;&ensp;&ensp;&ensp;下图将所有数据进行了[滑动平均MA]()操作，\
            也就是每天的数值取过去10天的平均值替代。这种方法可以减少原来时间序列中的短期波动，更加直观地了解整个聊天数的变动趋势。笑笑这两张图就是做了这样一件事情。把具体的数量叠加到假期/学期中。展示如下。")
    slt.markdown(
        "&ensp;&ensp;&ensp;&ensp;这里聊天总量的波动趋势更加明显。在寒暑假时期有很明显的波峰。并且，假期前由于考试等原因，都会短暂陷入波谷，尔后在假期开始后迅速爬升。两次聊天峰值均在假期中出现；而上学阶段由于每天黏在一起，也没有那么多说不完的话，聊天量趋于稳定，相当部分时间的聊天量不足平均数。")
    temp_pd = pd.DataFrame({"She": MACRO_DATA[2], "Time": EVERY_DAY})
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
                   symbol=None,
                   markpoint_opts=opts.MarkPointOpts(
                       data=[opts.MarkPointItem(type_="max")]),
                   markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(
                       type_="average")], label_opts=opts.LabelOpts(is_show=False)),
                   areastyle_opts=opts.AreaStyleOpts(
                       opacity=0.2, color="rgba(245,212,217,0.15)"),
                   )
        .set_series_opts(
            markarea_opts=opts.MarkAreaOpts(
                data=[
                    opts.MarkAreaItem(name="上学🎒", x=("2021-10-08", "2022-01-13"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(245,212,217,0.15)')),
                    opts.MarkAreaItem(name="放寒假🥳", x=("2022-01-13", "2022-02-12"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(241,158,194,0.25)')),
                    opts.MarkAreaItem(name="上学🎒", x=("2022-02-12", "2022-06-25"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(245,212,217,0.15)')),
                    opts.MarkAreaItem(name="放暑假🥰", x=("2022-06-25", "2022-08-17"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(241,158,194,0.25)')),
                    opts.MarkAreaItem(name="上学🎒", x=("2022-08-17", "2022-12-15"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(245,212,217,0.15)')),
                    opts.MarkAreaItem(name="放寒假😘", x=("2022-12-15", "2023-02-12"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(241,158,194,0.25)')),
                    opts.MarkAreaItem(name="上学🎒", x=("2023-02-12", "2023-03-27"),
                                      itemstyle_opts=opts.ItemStyleOpts(color='rgba(245,212,217,0.15)')),
                ]
            ),
            label_opts=opts.LabelOpts(is_show=False),
        )

        .set_global_opts(
            # datazoom_opts=[opts.DataZoomOpts()],
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),
            title_opts=opts.TitleOpts(title="对话总量的滑动平均(MA)", subtitle="WeChat骚话大赏!",
                                      pos_left=0, pos_top=5),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),

            ),
            legend_opts=opts.LegendOpts(
                selected_mode="multiple", pos_left=100, pos_top=80),
            datazoom_opts=[
                opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
        )
    )

    st_pyecharts(a, height="450px")
    slt.markdown("> &ensp;&ensp;&ensp;&ensp;如果把每天的聊天量和星期、时间周期结合起来看，就可以得到下面这个3D柱状图，反映一周不同时间段我们的聊天偏好，如下：")


show_rolling_window()


def show_heat_graph():
    average_per_day = len(CHAT_HISTORY) // (24 * 7)
    record_max = record_min = 0
    for i in range(len(WEEK_DAY_CNT)):

        # WEEK_DAY_CNT[i][2] -= average_per_day
        if record_max < WEEK_DAY_CNT[i][2]:
            record_max = WEEK_DAY_CNT[i][2]
        if record_min > WEEK_DAY_CNT[i][2]:
            record_min = WEEK_DAY_CNT[i][2]

    # print(WEEK_DAY_CNT)
    # for i in range(len(WEEK_DAY_CNT)):
    #     if WEEK_DAY_CNT[i][2] >= 0:
    #         WEEK_DAY_CNT[i][2] = (100 * WEEK_DAY_CNT[i][2])/record_max
    #     if WEEK_DAY_CNT[i][2] < 0:
    #         WEEK_DAY_CNT[i][2] =(-100 * WEEK_DAY_CNT[i][2])/record_min
    new_c = Bar3D()
    hours = [f"{i}时" for i in range(24)]
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    new_c.add(
        series_name="微信聊天总量",
        data=WEEK_DAY_CNT,
        xaxis3d_opts=opts.Axis3DOpts(type_="category", data=hours),
        yaxis3d_opts=opts.Axis3DOpts(type_="category", data=days),
        zaxis3d_opts=opts.Axis3DOpts(type_="value"),
    )
    new_c.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=record_max + 1,
            min_=record_min - 1,
            range_color=[
                "#313695",
                "#4575b4",
                "#74add1",
                "#abd9e9",
                "#e0f3f8",
                "#ffffbf",
                "#fee090",
                "#fdae61",
                "#f46d43",
                "#d73027",
                "#a50026",
            ],
        )
    )
    # c = (
    #     HeatMap(init_opts=opts.InitOpts(height="600px"))
    #     .add_xaxis([str(i) for i in range(24)])
    #     .add_yaxis(
    #         "",
    #         ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    #         WEEK_DAY_CNT,
    #         label_opts=opts.LabelOpts(is_show=True, position="inside"),
    #     )
    #     .set_global_opts(
    #         tooltip_opts=opts.TooltipOpts(
    #             trigger="item", axis_pointer_type="cross"),
    #         title_opts=opts.TitleOpts(title="星期-时间热力图"),
    #         visualmap_opts=opts.VisualMapOpts(
    #             min_=record_min - 1, max_=record_max + 1, is_calculable=True, orient="horizontal",
    #             pos_left="center", type_="color", range_opacity=0.9, precision=0, dimension=2),
    #     )
    # )
    bar_ = (
        Bar(init_opts=opts.InitOpts(height="600px"))
        .add_xaxis(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        .add_yaxis("消息数量", WEEKDAY_MSGS, color="#5793f3")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="星期分布"),

        )
    )
    bar2 = (
        Bar(init_opts=opts.InitOpts(height="600px"))
        .add_xaxis(["{}时".format(i) for i in range(24)])
        .add_yaxis("消息数量", HOURS_MSGS, color="#d14a61",
                   markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")], label_opts=opts.LabelOpts(is_show=False)))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="时间分布", pos_bottom="50%"),
            brush_opts=opts.BrushOpts(),
        )
    )

    grid = Grid(init_opts=opts.InitOpts(width="700px", height="1200px"))
    grid.add(bar_, grid_opts=opts.GridOpts(pos_bottom="55%"))
    grid.add(bar2, grid_opts=opts.GridOpts(pos_top="55%"))

    st_pyecharts(new_c)

    slt.write("""
    > &ensp;&ensp;&ensp;&ensp;这张图有点装B了，不过当我试着移动视角的时候，上帝啊，我想起了基础工业工程实验那门课上那个人因工程建模软件Jack。
    > 
    > &ensp;&ensp;&ensp;&ensp;本来画了一张日历图，后来觉得不够形象，就改成了一个3D的日历图。X / Y / Z轴分别代表0～24小时，星期一至星期天，在X，Y时间段发送消息的数量。这是一种方便地展现我们聊天倾向的方法。
    - 比如上述图表中x = 0,y = 0,z = 4668，意味着在所有周一晚上0点到1点之间，我们共发送了4668条消息
    """)
    slt.markdown(
        "> &ensp;&ensp;&ensp;&ensp;出乎预料的是，我们在周一的0点至1点聊天的数量最多（4868），看起来周一要么充满了槽点，要么我们都精力旺盛；而周一和周三的4点到5点的聊天数量最少（截至目前依然是0）。\n > 我更惊讶的一件事是，在每周7天的24小时中（168个时间区间），我们只有两个时间段没有聊过天😯！那么那些深度熬夜的日子我们在干什么呢？")
    slt.markdown(
        "> &ensp;&ensp;&ensp;&ensp;如果我们再做得细节一点，把一周七天的聊天量/一天每个时间段的聊天数量单独拎出来。能看到其他一些更加有意思的细节。比如下图。")
    st_pyecharts(grid, height="550px")
    slt.markdown(
        "> &ensp;&ensp;&ensp;&ensp;我们每周聊天记录的分布并不是十分均匀，即使是工作日，也说不上平稳。比如周二是\"吐槽大会\"召开的时间，总共有37000+条消息是在周二发出的。如果结合上面的图，你会发现周二也是我们经常熬夜聊天的日子（1点到2点之间）。同样的现象也发生在周五的晚上。我们在2点到3点间还在絮絮叨叨，说个不停。")

    slt.markdown(
        "> &ensp;&ensp;&ensp;&ensp;如果把重点转向每天的24小时，除开刚刚提到的23点～2点的时间区间，在15点与21点两个关键节点也会出现“驼峰”，笑笑猜想一方面是下午上课、下课的交流，导致信息增多，另一方面是晚上回到宿舍的时间点，往往是我们谈谈心事互相吐槽的开始。")

    slt.markdown("""
    --------

    > &ensp;&ensp;&ensp;&ensp;上面就是对所有数据的一个基础分析。下面瑜瑜可以移步笑笑的NLP与Emoji研究所，看看聊天记录里的文本/表情包是怎么透露这平淡日子里的点点滴滴的～
                 """)


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
