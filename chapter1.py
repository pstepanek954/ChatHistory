import streamlit as slt
import datetime
import json
import time
import pandas as pd
import numpy as np
import pytz
from collections import defaultdict
import pyecharts.options as opts
from pyecharts.charts import Line
from streamlit_echarts import st_pyecharts


slt.set_page_config(
    page_title="奇奇怪怪的发电中心站",   
    page_icon="🦈",  
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }      
    
)



slt.sidebar.header("About")





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
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray )
    return otherStyleTime



def get_local_timestamp(date_time):
    """ 返回本地时间的时间戳格式

    Args:
        date_time (_type_): _description_

    Returns:
        _type_: _description_
    """
    time_zone = pytz.timezone('Asia/Shanghai')
    timeArray = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    local_dt = timeArray.astimezone(time_zone)
    return int(time.mktime(local_dt.timetuple()))


@slt.experimental_memo # experimental_memo 这个处理缓存效果比cache要好得多
def load_data(address):
    temp = ""
    max_msg_vol = 0
    max_msg_date = 0
    

    with open(address, "r", encoding = "utf8")  as f:
        temp = json.load(f) # 加载数据

    messenger = defaultdict(def_value) # 消息总数
    types = defaultdict(def_value_list) # 消息的种类：按照分类进行排布
    
    left = temp[0]["CreateTime"] # 开始时间（精确到秒）
    right = temp[-1]["CreateTime"] # 结束时间(精确到秒)

    left_day_ymd = get_local_time_ymd(left) # 获取第一天的 "%y-%m-%d" string
    right_day_ymd = get_local_time_ymd(right) # 获取最后一天的 "%y-%m-%d" string

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
    for idx, i in enumerate(temp): # 统计消息数量
        messenger[i["Des"]] += 1
        types[i["Type"]][i["Des"]] += 1
        if start_idx + 1 < len(every_day_timestamp) and i["CreateTime"] < every_day_timestamp[start_idx + 1]:
            every_day_detail[every_day[start_idx]][i["Type"]][i["Des"]] += 1
        elif start_idx + 1 < len(every_day_timestamp) and i["CreateTime"] >= every_day_timestamp[start_idx + 1]:
            if max_msg_vol < (idx - tmp_idx):
                max_msg_date = every_day[start_idx]
                max_msg_vol = idx - tmp_idx
            tmp_idx = idx
            start_idx += 1
            every_day_detail[every_day[start_idx]] = defaultdict(def_value_list)
            every_day_detail[every_day[start_idx]][i["Type"]][i["Des"]] += 1
        else:
            if len(temp) - idx > max_msg_vol:
                max_msg_vol = len(temp) - idx
                max_msg_date = every_day[-1]
            tail[i["Type"]][i["Des"]] += 1
            
    every_day_detail[every_day[-1]] = tail

    return temp, messenger, left, right, types, every_day, every_day_timestamp, every_day_detail, max_msg_date, max_msg_vol



def def_value():
    return 0
def def_value_list():
    return [0, 0]


ADDRESS = "./chathistory.json"
CHAT_HISTORY, TOTAL_CNT, START_TIMESTAMP, END_TIMESTAMP, TYPES_CNT, EVERY_DAY, \
    EVERY_DAY_TIMESTAMP, EVERY_DAY_DETAIL, MAX_MSG_DATE , MAX_MSG_VOL = load_data(ADDRESS)


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

slt.markdown("# 奇奇怪怪的聊天站")
slt.caption("🧐 什么聊天站！进来看看！")


slt.json(CHAT_HISTORY[-1])

# ============================ ==================================



def get_msg_vol(timestamp1, timestamp2):
    start = 0
    end = TOTAL_MSG - 1
    indx1 = -1
    indx2 = -1
    while start <= end:
        mid = start + ((end - start) >> 1)
        if CHAT_HISTORY[mid]['CreateTime'] > timestamp1:
            indx1 = mid
            end = mid - 1
        else:
            start = mid + 1
    start = 0
    end = TOTAL_MSG - 1
    while start <= end:
        mid = start + ((end - start) >> 1)
        if CHAT_HISTORY[mid]['CreateTime'] > timestamp2:
            indx2 = mid
            end = mid - 1
        else:
            start = mid + 1
    return int(abs(indx1 - indx2))


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
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

def show_profile():
    slt.write("总共有", str(TOTAL_MSG) ,"条消息, 最早的消息来自瑜瑜子，发送时间是", \
        get_local_time(START_TIMESTAMP), "而最晚的消息是笑笑在", get_local_time(END_TIMESTAMP) , \
            "发送的。", "在这", str(get_interval_time(START_TIMESTAMP, END_TIMESTAMP)), "天中，我们畅所欲言，无话不谈。"  )
    slt.write("记录显示，在", MAX_MSG_DATE, "这一天，我们是两只大话痨，一共发送了", MAX_MSG_VOL, "条消息，是有史以来最多的一天，\
        这意味着那24个小时里，我们每隔1分钟就会发送消息。" )

show_profile()

d = slt.sidebar.date_input(
    "🛩️  聊天记录查询站｜选个日子！ :kiss:",
    datetime.date(2022, 2, 3))
slt.sidebar.write('你选择的日期 📅 是:', d)
slt.sidebar.write("Msg volume for the selected day " , d, " is ", get_msg_vol(get_local_timestamp(str(d) + " 00:00:00"), \
     get_local_timestamp(str(d) + " 23:59:59")))
slt.sidebar.markdown("------")
# slt.write(EVERY_DAY_DETAIL[str(d)])



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
    input_data = [[0 for _ in range(len(EVERY_DAY))] for _ in range(3)]
    for day, i in enumerate(EVERY_DAY):
        cur_dict = EVERY_DAY_DETAIL[i]
        for j in cur_dict:
            input_data[0][day] += cur_dict[j][0]
            input_data[1][day] += cur_dict[j][1]
        input_data[2][day] = input_data[0][day] + input_data[1][day]

    c = (
        Line()
        .add_xaxis(EVERY_DAY)
        .add_yaxis("天瑜的!",
                input_data[1], 
                is_smooth=True, 
                symbol = None,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]),
                areastyle_opts=opts.AreaStyleOpts(opacity=0.2, color="rgba(245,212,217,0.15)"),
                )
        .add_yaxis("笑笑的!", 
                input_data[0], 
                is_smooth=True, 
                symbol = None,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]))
        .add_yaxis("一起的!", 
                input_data[2],
                is_smooth=True,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")] ),
                markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]))
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            # markarea_opts=opts.MarkAreaOpts(
            #     data=[
            #         opts.MarkAreaItem(name="上学期！", x=("2021-10-08", "2022-01-13")
            #                         ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(245,212,217,0.15)')),
            #         opts.MarkAreaItem(name="这里是寒假！", x=("2022-01-13", "2022-02-12")
            #                         ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(249,204,226,0.15)')),
            #         opts.MarkAreaItem(name="下学期！", x=("2022-02-12", "2022-03-18")
            #                         ,itemstyle_opts = opts.ItemStyleOpts(color = 'rgba(241,158,194,0.1)')),
            #     ]
            # ),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            title_opts=opts.TitleOpts(title="对话数量",subtitle="WeChat骚话大赏!",
                                    pos_left=50, pos_top=10),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            legend_opts = opts.LegendOpts( selected_mode="multiple",pos_left=100,pos_top=80)
        )
        
    )
    st_pyecharts(c, height="650px")
show_marco_line_graph()
    
    
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



# slt.write("Time stamp is ", str(get_local_timestamp( "2022-10-04 10:57:22")))
# print(d)
# ============================== ============================== 


# import streamlit as st
# import pandas as pd
# import numpy as np

# st.title('Uber pickups in NYC')

# DATE_COLUMN = 'date/time'
# DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
#             'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

# @slt.cache
# def loads_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data

# data_load_state = slt.text('Loading data...')
# data = loads_data(10000)
# data_load_state.text("Done! (using st.cache)")

# if slt.checkbox('Show raw data'):
#     slt.subheader('Raw data')
#     slt.write(data)

# slt.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# slt.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = slt.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# slt.subheader('Map of all pickups at %s:00' % hour_to_filter)
# slt.map(filtered_data)



# ============================== ============================== 
# d = slt.date_input(
#     "When\'s your birthday",
#     datetime.date(2019, 7, 6))
# slt.write('Your birthday is:', d)

# slt.info(len(CHAT_HISTORY))
# def run():
# chat_history = load_data(ADDRESS)
# slt.write(len(chat_history))
# slt.title("Tutorials Streamlit")
# slt.info("Hello fellow!")
# slt.header("Header")
# slt.subheader("SubHeader")
# slt.success("Success")
# slt.warning("Warning")
# slt.markdown("$$  f(x) = x$$")
# slt.write("Write here.")
# # img = Image.open("picx1.png")
# # slt.image(img, width= 300, caption="picx1")

# chat_history = load_data(ADDRESS)


# occupation = slt.selectbox("Your occupation", ["Ds", "farmer", "Teacher"])
# slt.write(occupation)

# location = slt.multiselect("Where do you work?", ["Beijing", "Shanghai", "Chengdu"])
# slt.write("You select " , len(location), " Locations")
# level = slt.slider("Whats your level?", 2,100)

# first_name = slt.text_input("Your first name?", "Type here..") 
# result = ""
# if slt.button("Submit"):
#     result = first_name.title()
#     slt.success(result)

# chat_history = None
# with open("./chathistory.json", "r", encoding = "utf8") as f:
#     chat_history = json.load(f)

# slt.write(len(chat_history))


#     today = slt.date_input("Today is ", datetime.datetime.now())

#     time_ = slt.time_input("Time is ", datetime.time())

#     slt.json({"Name" : result, "Age" : level})

#     my_bar = slt.progress(0)
#     for p in range(10):
#         my_bar.progress(p + 1)

#     # slt.balloons()
# # sudo rm -rf /Library/Developer/CommandLineTools
# #   sudo xcode-select --install
#     slt.sidebar.header("About")


# slt.sidebar.write(len(chat_history))

# if __name__ == "__main__":
#     run()