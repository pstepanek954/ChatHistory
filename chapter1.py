import streamlit as slt
import datetime
import json
import time
import pandas as pd
import numpy as np
import pytz
from collections import defaultdict


slt.set_page_config(
    page_title="奇奇怪怪的发电中心站",   
    # page_icon=":rainbow:",        
    # layout="wide",                
    # initial_sidebar_state="auto"  
)

if 'first_visit' not in slt.session_state:
    slt.session_state.first_visit=True
else:
    slt.session_state.first_visit=False
if slt.session_state.first_visit:
    slt.balloons()  #第一次访问时才会放气球

@slt.experimental_memo
def load_data(address):
    temp = ""
    max_msg_vol = 0
    with open(address, "r", encoding = "utf8")  as f:
        temp = json.load(f)

    messenger = defaultdict(def_value) # 消息总数
    types = defaultdict(def_value_list) # 消息的种类：按照分类进行排布
    
    left = temp[0]["CreateTime"]
    right = temp[-1]["CreateTime"]

    for i in temp:
        messenger[i["Des"]] += 1
        types[i["Type"]][i["Des"]] += 1
    return temp, messenger, left, right, types


def def_value():
    return 0
def def_value_list():
    return [0, 0]


ADDRESS = "./chathistory.json"
CHAT_HISTORY, TOTAL_CNT, START_TIMESTAMP, END_TIMESTAMP, TYPES_CNT = load_data(ADDRESS)



def TYPES_CNT_process():

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
    msg_idx = [1, 47, 49, 3, 34, 10002, 43, 10000, 50, 48, 42 ]
    msg_del = [TYPES_CNT[i][0] for i in msg_idx]
    msg_rec = [TYPES_CNT[i][1] for i in msg_idx]
    TYPES_CNT_dataframe = pd.DataFrame({ "消息类型":["文字消息", "表情包", "消息引用｜外链分享", "图片消息", "语音消息", \
        "消息撤回", "视频消息", "红包/拍一拍等系统消息", "VX通话", "定位分享", "联系人推荐"], "瑜瑜子的": np.array(msg_rec),\
             "笑笑子的": np.array(msg_del), "总计": np.array(msg_del) + np.array(msg_rec) })
    return TYPES_CNT_dataframe
    
#  = basic_count(CHAT_HISTORY)
# START_TIMESTAMP = CHAT_HISTORY[0]['CreateTime']
# END_TIMESTAMP = CHAT_HISTORY[-1]['CreateTime']
TOTAL_MSG = len(CHAT_HISTORY)

slt.markdown("# 奇奇怪怪的聊天站")
slt.json(CHAT_HISTORY[-1])

# ============================ ==================================



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

show_profile()

d = slt.date_input(
    "Choose Start Day :kiss:",
    datetime.date(2022, 2, 3))
slt.write('你选择的日期 📅 是:', d)
slt.write("Msg volume for the selected day " , d, " is ", get_msg_vol(get_local_timestamp(str(d) + " 00:00:00"), \
     get_local_timestamp(str(d) + " 23:59:59")))

# slt.write(TOTAL_CNT[0])

df = pd.DataFrame(
   np.random.randn(10, 5),
   columns=('col %d' % i for i in range(5)))


TYPES_CNT_dataframe = TYPES_CNT_process()
slt.table(TYPES_CNT_dataframe)
slt.write([[i, TYPES_CNT[i][0], TYPES_CNT[i][1]] for i in TYPES_CNT])

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