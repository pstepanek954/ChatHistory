import streamlit as st
import json
import sqlite3
import os
from streamlit_echarts import st_pyecharts


import time
import datetime
from collections import Counter
import pandas as pd 
from pyecharts import options as opts
from pyecharts.charts import Bar



def get_local_time_ten(timeStamp):
    """ 从时间戳获取当地时间

    Args:
        timeStamp (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    t  = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", t.timetuple())[:10]
    return otherStyleTime

def timestamp_2_date(n):
    return get_local_time_ten(n[0])

os.environ['TZ'] = 'Asia/Shanghai'
CONN = sqlite3.connect('./static/files/chathistory.db')

EVERY_DAY = st.session_state.every_day

def run_query(query_sentence):
    cur = CONN.cursor()
    
    query = f"select createTime, Des from chathistory where Message like \"%{query_sentence}%\" "
    t = cur.execute(query).fetchall()
    
    st.write("总共出现了：", str(len(t)), "次！")


    res = list(map(timestamp_2_date, t))
    cnt_mac = Counter(res)
    # x_axis = []
    y_axis = []
    for i in EVERY_DAY:
        y_axis.append(cnt_mac[i])
    
    c = (
        Bar()
        .add_xaxis(EVERY_DAY)
        .add_yaxis(
        "数量", 
        y_axis, 
        category_gap=0,
        label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
        title_opts=opts.TitleOpts(
        title=f"那些说'{query_sentence}'的日子"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),)
    )

    st_pyecharts(c, height="350px")

# .set_global_opts(
#             yaxis_opts=opts.AxisOpts(
#                 type_="value",
#                 name=legend_list[1],
#                 min_=0, 
#                 max_=max(input_df["EMOJIS"]) + 50,
#                 position="right",
#                 offset=80,
#                 axisline_opts=opts.AxisLineOpts(
#                     linestyle_opts=opts.LineStyleOpts(color=colors[0])
#                 ),
#                 axislabel_opts=opts.LabelOpts(formatter="{value} ml"),
#             ),
#             tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
#         )

content = st.text_input('找找这句话！', '')
if len(content) > 0:
    run_query(content)

# cur_time = time.perf_counter()
# cur = CONN.cursor()
# t1 = "select createTime, Des, Message, Type from chathistory"
# t2 = cur.execute(t1).fetchall()


CONN.close()

# # Perform query.
# # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
# def run_query(query):
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchall()

# rows = run_query("SELECT CreateTime, Message from chathistory where Des = 0;")

# # Print results.
# for row in rows[2:30]:
#     st.write(f"{row[0]} said: {row[1]} ")

st.write("Database  Test")