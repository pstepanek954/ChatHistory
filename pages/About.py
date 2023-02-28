import pandas as pd
import streamlit as slt
import datetime
import time
import re
from PIL import Image
from collections import defaultdict, Counter
import pyecharts.options as opts
from pyecharts.charts import Line, HeatMap, Grid, Bar
import base64
import random
from streamlit_echarts import st_pyecharts
import os
import math
import numpy as np
import matplotlib.pyplot as plt

# from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# from statsmodels.tsa.stattools import adfuller as adf 
# from statsmodels.stats.diagnostic import acorr_ljungbox as lbtest
# from statsmodels.tsa.arima.model import ARIMA

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

def get_local_timestamp(date_time):
    """ 返回本地时间的时间戳格式

    Args:
        date_time (_type_): _description_

    Returns:
        _type_: _description_
    """
    timeArray = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timeArray.timetuple()))

slt.header("这里是！🤔笑笑的表情包研究所！")

EV_DAY_EMOJIS = slt.session_state.emoji_packs

def return_zero():
    return 0

EMOJI_TYPES = defaultdict(return_zero)
EMOJI_INCREMENT = defaultdict(return_zero)
EVERY_DAY = slt.session_state.every_day
EVERY_DAY_DETAIL = slt.session_state.every_day_detail

def EMOJI_ANALYSIS():
    
    idxx = 0
    idxx_2 = 0
    quantity_idx_2 = 0

    emoticon_creaters = Counter()

    for i in EV_DAY_EMOJIS:
        if "productid=\"com.tencent.xin.emoticon.person.stike" in i[2]:
            idxx += 1
            location = i[2].find('productid=\"com.tencent.xin.emoticon.person.stiker')
            emoticon_creaters[i[2][location + 50:location+76]] += 1
            
        if "thumburl = \"http://mmbiz.qpic.cn/" in i[2]:
            idxx_2 += 1
        if "type=\"2\"" in i[2]:
            quantity_idx_2 += 1
        # elif "type=\"1\"" in i["Message"]:
        #     quantity_idx_1 += 1
        # elif "type=\"3\"" in i["Message"]:
        #     quantity_idx_3 += 1
        if "<gameext type=\"2\"" in i[2] and "type=\"2\"" not in i[2]:
            quantity_idx_2 -= 1
        # if "<gameext type=\"1\"" in i["Message"] and "type=\"1\"" not in i["Message"]:
        #     quantity_idx_1 -= 1
        # if "<gameext type=\"3\"" in i["Message"] and "type=\"3\"" not in i["Message"]:
        #     quantity_idx_3 -= 1
    
    slt.write("瑜瑜应该还记得我之前一版的聊天记录分析里，对我们使用过的表情包和Emoji进行了简要的分析，这一部分就是一个更加细致的研究！")
    slt.markdown("## 表情包")
    slt.write("完全统计表明，总共", str(len(EV_DAY_EMOJIS)), "条表情包交互中，有",str(quantity_idx_2),"条(", str(round(100 * quantity_idx_2/len(EV_DAY_EMOJIS), 2)), "%)来自创作者制作的表情，剩下不到",str( round(101 - 100 * quantity_idx_2/len(EV_DAY_EMOJIS), 0)), "%是自定义/从图片中改造的表情。")
    # slt.markdown("> 🧐 看来咱们还是喜欢乱动的可爱小玩意儿")
    slt.write("下面这张图把这些消息拉长到整个", str(len(EVERY_DAY)), "天的时间维度上，看看我们对表情包的喜好如何——")
    slt.markdown("- 和最开始一样，笑笑对数据做了一个滑动平均，每一天的实际表情包发送量取了过去10天之期望，这样把整体趋势更好滴表现出来～")
    slt.write('most common creaters: ', emoticon_creaters.most_common(10))
    slt.write("BongBong 兔！（按摩）/ 动起来的BongBong兔（）/小八狗）")
def get_daily_emoji():
    EMOJI_ANALYSIS()
    emoji_cnts = dict()
    total_msg_cnt = []
    
    for i in EVERY_DAY:
        tmp = 0
        for k in EVERY_DAY_DETAIL[i]:
            tmp += (EVERY_DAY_DETAIL[i][k][0] + EVERY_DAY_DETAIL[i][k][1])
        total_msg_cnt.append(tmp)

    for i in EVERY_DAY:
        emoji_cnts[i] = 0
    
    emoji_appeared = set() # 日期指针
    
    for i in EV_DAY_EMOJIS:
        cur_day = get_local_time_ymd(i[0])[:10]
        cur_emoji = i[2]

        
        emoji_name = re.findall('md5=\"(.*?)"', cur_emoji)[0] 
        if emoji_name not in emoji_appeared:
            emoji_appeared.add(emoji_name)
            EMOJI_INCREMENT[cur_day] += 1
        EMOJI_TYPES[emoji_name] += 1    
        emoji_cnts[cur_day] += 1
    
    input_df = pd.DataFrame({"Time" : EVERY_DAY, "EMOJIS": [emoji_cnts[i] for i in EVERY_DAY]})
    input_df["Rolling" ]=  input_df["EMOJIS"].rolling(10).mean()
    input_df["TOTAL_MSG"] = total_msg_cnt
    input_df.index = input_df["Time"]
    input_df["Percent"] = input_df.apply(lambda x: x['EMOJIS'] /  x['TOTAL_MSG'], axis=1)

    input_df['Percent'] = input_df['Percent'].apply(lambda x: format(x, '.2f'))

    colors = ["#5793f3", "#d14a61", "#675bba"]
    legend_list = ["Emoji滑动平均", "Emoji总量", "表情包浓度"]
    
    bar = (
        Bar(init_opts=opts.InitOpts(width="1260px", height="720px"))
        .add_xaxis(xaxis_data=list(input_df["Time"]))
        .add_yaxis(
            series_name="Emoji数量", y_axis=list(input_df["EMOJIS"]), yaxis_index=0, color=colors[1], category_gap=0,
        )
        .add_yaxis(
            series_name="Emoji滑动平均", y_axis=list(input_df["Rolling"]), yaxis_index=1, color=colors[0], category_gap=0,
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name=legend_list[0],
                type_="value",
                min_=0,
                max_=max(input_df["Rolling"]) + 50,
                position="right",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color=colors[1])
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} 条"),
            )
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                name=legend_list[2],
                min_=float(min(input_df["Percent"])) - float(max(input_df["Percent"])),
                max_=max(input_df["Percent"]),
                position="left",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color=colors[2])
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                ),
            )
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name=legend_list[1],
                min_=0, 
                max_=max(input_df["EMOJIS"]) + 50,
                position="right",
                offset=80,
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color=colors[0])
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} ml"),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        )
    )

    line = (
        Line()
        .add_xaxis(xaxis_data=list(input_df["Time"]))
        .add_yaxis(
            series_name="表情包浓度", y_axis=list(input_df["Percent"]), yaxis_index=2, color=colors[2]
        )
    )
    bar.overlap(line)
    grid = Grid()
    grid.add(bar, opts.GridOpts(pos_left="5%", pos_right="20%"), is_control_axis_index=True)

    st_pyecharts(grid)

    slt.write("这里说一个非常非常巧合的事情。我的前一个聊天记录分析网站，数据截止到2022年3月18日，就在这一天之后，也就是2022-03-19，\
        我们的表情包浓度突然特别高——数字离谱到我甚至有些不敢相信：", max(input_df["Percent"]), "！")
    slt.markdown("> 🧐 要知道浓度第二高的日子里，表情包占比都没有超过23%...\n这意味着那一天我们有超过三分之一的对话是用表情包来表示的，更可怕的是，这还是算入了笑笑碎碎念一般的消息在内的比例。")
    
    slt.write("于是好奇心驱使我去看了看那天具体的聊天记录📝，画风是这样的：")
    slt.markdown("> 哈哈哈哈哈！")

    slt.write("另外一个很好玩的事情是，除了我们相遇、相聊、相互喜欢前的暧昧期外，我们从2021年10月18日后，只有一天没有发送表情包：2022年2月27日。那一天一定发生了很多，我们忙着见面，少用表情包传达感情。")
    
    return input_df
    
INPUT_DF = get_daily_emoji()

def emoji_type_analysis():
    # print(len(EMOJI_TYPES))
    emoji_type =  sorted(EMOJI_TYPES.items(),key = lambda x:x[1],reverse = True)
    a = 0
    for i in range(10):
        slt.write(emoji_type[i])
    slt.info("因为技术原因，微信本地没有提供明文状态的表情包图片，\
        相关数据经过加密后存储在文本文件中。通过一些溯源手段笑笑获取了所有的加密文件，但是由于不知如何破解\
            ，所以最终无法通过聊天记录文本直接对应到图片。这直接导致工作量迅速增加。因为笑笑只能先得到一个md5加密后的序列，然后到聊天记录中对应消息出现的位置，\
                最后确定表情是哪一个。这种Hard Code的方式实在不讨我喜。")
    slt.markdown("下面是一段加密后呈现乱码的表情包文件的实例：")
    with open("./static/files/51b609ce8f40f68bcb387dbf96d74059", "rb") as file:
        btn = slt.download_button(
                label="点击下载乱码",
                data=file,
                file_name="51b609ce",
        )
    Rank1 = Image.open("./static/pics/嗷呜rank1.png")
    Rank2 = Image.open("./static/pics/嘿嘿rank3.png")
    Rank3 = Image.open("./static/pics/嘿嘿rank5.png")
    Rank4 = Image.open("./static/pics/嘿嘿rank7.png")
    Rank5 = Image.open("./static/pics/动画表情rank8.png")
    Rank6 = Image.open("./static/pics/嘿嘿rank9.png")
    Rank7 = Image.open("./static/pics/害羞rank10.png")

    slt.markdown("下图展示了使用次数最多的10张表情：")

    slt.image([Rank1, Rank2, Rank3, Rank4, Rank5, Rank6, Rank7],width = 134)
    
    
    file_1 = open("./static/pics/开心rank2.gif", "rb")
    contents = file_1.read()
    data_url_1 = base64.b64encode(contents).decode("utf-8")
    file_1.close()

    file_2 = open("./static/pics/按摩rank4.gif", "rb")
    contents = file_2.read()
    data_url_2 = base64.b64encode(contents).decode("utf-8")
    file_2.close()

    file_3 = open("./static/pics/搞砸rank6.gif", "rb")
    contents = file_3.read()
    data_url_3 = base64.b64encode(contents).decode("utf-8")
    file_3.close()
# {emoji_type[6][1]}, {emoji_type[7][1]}, {emoji_type[8][1]}, {emoji_type[9][1]}; \

    
    slt.markdown(
        f'<img src="data:image/gif;base64,{data_url_1}" alt="cat gif">\
        <img src="data:image/gif;base64,{data_url_2}" alt="cat gif"> \
         <img src="data:image/gif;base64,{data_url_3}" alt="cat gif">',
        unsafe_allow_html=True,
    )
    slt.markdown("两行依次是：")
    slt.markdown(f"- [嗷呜] ({emoji_type[0][1]}次)、[嘿嘿] ({emoji_type[2][1]}次)、 [嘿嘿] ({emoji_type[4][1]}次)、\
        [嘿嘿] {emoji_type[6][1]}次、[动画表情] ({emoji_type[7][1]}次)、[嘿嘿] ({emoji_type[8][1]}次)、[害羞] ({emoji_type[9][1]}次) ")
    slt.markdown(f"- [开心] ({emoji_type[1][1]}次)、 [按摩] ({emoji_type[3][1]}次)、 [砸了] ({emoji_type[5][1]}次)")
    slt.markdown("使用次数最多的表情包\" 嗷呜 \" ，在上一次的统计中出现次数也是最多的（270次），但是这次和第二位（263）的距离缩小了很多。")
    slt.markdown("很有趣的一个细节是，前10个常用表情里，有4个都是\"嘿嘿\"。这个语气词一定是我们最经常想要借助表情包表达的～")
    
    bar3 = (
        Bar(init_opts=opts.InitOpts())
        .add_xaxis(xaxis_data=list(EVERY_DAY))
        .add_yaxis(
            series_name="Emoji数量", y_axis=[EMOJI_INCREMENT[i] for i in EVERY_DAY], category_gap=0,
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
    )
    st_pyecharts(bar3)
       
emoji_type_analysis()

# def TimeSeries_analysis():
#     temp_ipt = INPUT_DF
#     temp_ipt.index = [(i+ 1) for i in range(len(EVERY_DAY))]
    
#     del temp_ipt["Time"]
#     del temp_ipt["Rolling"]
#     # print(temp_ipt)
#     test = adf(temp_ipt, autolag="AIC")
    
#     # print("P-value = {}".format(test[1]) )

# for i in EVERY_DAY:
#     print(i)