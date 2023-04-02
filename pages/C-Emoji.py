# 这一部分是表情包统计


import pandas as pd
import streamlit as slt
import datetime
import time
import re
from PIL import Image
from collections import defaultdict, Counter
import pyecharts.options as opts
from pyecharts.charts import Line, HeatMap, Grid, Bar, Timeline
import base64
import random
from streamlit_echarts import st_pyecharts
import os
import math
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.stats.diagnostic import acorr_ljungbox as lb_test
from statsmodels.tsa.stattools import adfuller as adf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# from statsmodels.tsa.stattools import adfuller as adf
# from statsmodels.stats.diagnostic import acorr_ljungbox as lbtest
# from statsmodels.tsa.arima.model import ARIMA

os.environ['TZ'] = 'Asia/Shanghai'

NO1 = "66ff555af0033ee332d3b5540914d71b"
NO2 = "cbd8610ac858597def3e401a848a94e2"
NO3 = "4a06eb2177884ec05edc43ef2f721219"
NO4 = "41d2f01c7eb7451aee7f8987bcdab700"
NO5 = "1c610badc0e4ff27ecdaa0b802f4f241"
NO6 = "a9fba580a23fb794760adea045fa27eb"
NO7 = "cd4dc33d96b030063554e22cd02670a6"
NO8 = "2f3936cbc409df79a7f040f73fd192e4"
NO9 = "e2232dc6e973a21e8243050e6a58f980"
NO10 = "edb6978d023a7c11a9d54f294eafcc50"  # 是前10个使用量最多的表情包的MD5编号


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


slt.title("这里是！🤔笑笑的表情包研究所！")
slt.caption("⚠️ 所有的微信系统表情都没有计算在内，因为进行处理实在过于复杂了。")
slt.markdown("---------")

EV_DAY_EMOJIS = slt.session_state.emoji_packs


def return_zero():
    return 0


EMOJI_TYPES = defaultdict(return_zero)
EMOJI_INCREMENT = defaultdict(return_zero)
EVERY_DAY = slt.session_state.every_day
EVERY_DAY_DETAIL = slt.session_state.every_day_detail


EMOJI_TOP_TEN = [defaultdict(lambda: 0)
                 for _ in range(10)]  # 统计前10个最多的表情包出现的情况
emoticon_creaters = Counter()


def EMOJI_ANALYSIS():
    idxx = 0
    idxx_2 = 0
    quantity_idx_2 = 0

    for i in EV_DAY_EMOJIS:
        if "productid=\"com.tencent.xin.emoticon.person.stike" in i[2]:
            idxx += 1
            location = i[2].find(
                'productid=\"com.tencent.xin.emoticon.person.stiker')
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
    slt.markdown("## 表情（包）")
    slt.write("完全统计表明，总共", str(len(EV_DAY_EMOJIS)), "条表情包交互中，有", str(quantity_idx_2), "条(", str(round(100 * quantity_idx_2 /
              len(EV_DAY_EMOJIS), 2)), "%)来自创作者制作的表情，剩下不到", str(round(101 - 100 * quantity_idx_2/len(EV_DAY_EMOJIS), 0)), "%是自定义/从图片中改造的表情。")
    # slt.markdown("> 🧐 看来咱们还是喜欢乱动的可爱小玩意儿")
    slt.write("下面这张图把这些消息拉长到整个", str(len(EVERY_DAY)),
              "天的时间维度上，看看我们对表情包的喜好如何——")
    slt.markdown(
        "- 和最开始一样，笑笑对数据做了一个滑动平均，每一天的实际表情包发送量取了过去10天之期望，这样把整体趋势更好滴表现出来～")


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

    emoji_appeared = set()  # 日期指针

    for i in EV_DAY_EMOJIS:  # 计算每天的表情包的数量
        cur_day = get_local_time_ymd(i[0])[:10]
        cur_emoji = i[2]

        emoji_name = re.findall('md5=\"(.*?)"', cur_emoji)[0]
        if emoji_name not in emoji_appeared:
            emoji_appeared.add(emoji_name)
            EMOJI_INCREMENT[cur_day] += 1
        EMOJI_TYPES[emoji_name] += 1
        emoji_cnts[cur_day] += 1

        if NO1 in cur_emoji:  # 统计排名前10的表情包的情况
            EMOJI_TOP_TEN[0][cur_day] += 1
        elif NO2 in cur_emoji:
            EMOJI_TOP_TEN[1][cur_day] += 1
        elif NO3 in cur_emoji:
            EMOJI_TOP_TEN[2][cur_day] += 1
        elif NO4 in cur_emoji:
            EMOJI_TOP_TEN[3][cur_day] += 1
        elif NO5 in cur_emoji:
            EMOJI_TOP_TEN[4][cur_day] += 1
        elif NO6 in cur_emoji:
            EMOJI_TOP_TEN[5][cur_day] += 1
        elif NO7 in cur_emoji:
            EMOJI_TOP_TEN[6][cur_day] += 1
        elif NO8 in cur_emoji:
            EMOJI_TOP_TEN[7][cur_day] += 1
        elif NO9 in cur_emoji:
            EMOJI_TOP_TEN[8][cur_day] += 1
        elif NO10 in cur_emoji:
            EMOJI_TOP_TEN[9][cur_day] += 1

    input_df = pd.DataFrame({"Time": EVERY_DAY, "EMOJIS": [
                            emoji_cnts[i] for i in EVERY_DAY]})
    input_df["Rolling"] = input_df["EMOJIS"].rolling(10).mean()
    input_df["TOTAL_MSG"] = total_msg_cnt
    input_df.index = input_df["Time"]
    input_df["Percent"] = input_df.apply(
        lambda x: x['EMOJIS'] / x['TOTAL_MSG'], axis=1)

    input_df['Percent'] = input_df['Percent'].apply(lambda x: format(x, '.2f'))
    colors = ["#5793f3", "#d14a61", "#675bba"]
    legend_list = ["Emoji滑动平均", "Emoji总量", "表情浓度"]
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
                min_=float(min(input_df["Percent"])) -
                float(max(input_df["Percent"])),
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
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),
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
    grid.add(bar, opts.GridOpts(pos_left="5%", pos_right="20%"),
             is_control_axis_index=True)

    st_pyecharts(grid)

    slt.write("&ensp;&ensp;&ensp;&ensp;这里说一个非常非常巧合的事情。我的前一个聊天记录分析网站，数据截止到2022年3月18日，就在这一天之后，也就是2022-03-19，\
        我们的表情包浓度突然特别高——数字离谱到我甚至有些不敢相信：", max(input_df["Percent"]), "！")
    slt.markdown(
        "> &ensp;&ensp;&ensp;&ensp;🧐 要知道浓度第二高的日子里，表情包占比都没有超过26%...\n这还意味着那一天我们有超过三分之一的对话是用表情包来表示的（好抽象啊！）")

    slt.write("&ensp;&ensp;&ensp;&ensp;于是好奇心驱使我去看了看那天具体的聊天记录📝，画风是这样的：")
    emj_20220319 = Image.open("./static/pics/20220319.jpg")
    emj_202207201 = Image.open("./static/pics/20220720-1.jpg")
    emj_202202202 = Image.open("./static/pics/20220720-2.jpg")
    emoji_col1, emoji_col2, emoji_col3 = slt.columns(3)
    emoji_col1.image(emj_20220319)
    emoji_col2.image(emj_202207201)
    emoji_col3.image(emj_202202202)
    slt.markdown("> 哈哈哈哈哈！")

    slt.write("&ensp;&ensp;&ensp;&ensp;另外一个很好玩的事情是，除了我们相遇、相聊、相互喜欢前的暧昧期外，我们从2021年10月18日后，只有一天没有发送表情包：2022年2月27日。那一天一定发生了很多，我们忙着见面，少用表情包传达感情。")

    return input_df


INPUT_DF = get_daily_emoji()

# 展示使用次数最多的10个表情包


def display_most_used_authors():

    Author_1 = Image.open("./static/pics/One.jpg")
    Author_2 = Image.open("./static/pics/Two.jpg")
    Author_3 = Image.open("./static/pics/Three.jpg")
    Author_4 = Image.open("./static/pics/Four.jpg")
    Author_5 = Image.open("./static/pics/Five.jpg")
    Author_6 = Image.open("./static/pics/Six.jpg")
    Author_7 = Image.open("./static/pics/Seven.jpg")
    Author_8 = Image.open("./static/pics/Eight.jpg")
    Author_9 = Image.open("./static/pics/Nine.jpg")
    Author_10 = Image.open("./static/pics/Ten.jpg")

    slt.image([Author_1, Author_2, Author_3, Author_4, Author_5], width=200)
    slt.image([Author_6, Author_7, Author_8, Author_9, Author_10], width=200)

    tmp_top_10 = emoticon_creaters.most_common(10)
    slt.caption(f"分别被使用了{tmp_top_10[0][1]}, {tmp_top_10[1][1]}, {tmp_top_10[2][1]}, {tmp_top_10[3][1]}, {tmp_top_10[4][1]}, {tmp_top_10[5][1]}, {tmp_top_10[6][1]}, {tmp_top_10[7][1]}, {tmp_top_10[8][1]}, {tmp_top_10[9][1]} 次。")


def emoji_type_analysis():
    # print(len(EMOJI_TYPES))
    emoji_type = sorted(EMOJI_TYPES.items(), key=lambda x: x[1], reverse=True)
    # a = 0
    # for i in range(10):  # TODO： 这一行作用：在每次更新数据库后查看使用次数最多的表情包的md5加密编码；
    #     slt.write(emoji_type[i])
    slt.info("&ensp;&ensp;&ensp;&ensp;因为技术原因，微信本地没有提供明文状态的表情包图片，\
        相关数据经过加密后存储在文本文件中。通过一些溯源手段笑笑获取了所有的加密文件，但是由于不知如何破解\
            ，所以最终无法通过聊天记录文本直接对应到图片。这直接导致工作量迅速增加。因为笑笑只能先得到一个md5加密后的序列，然后到聊天记录中对应消息出现的位置，\
                最后确定表情是哪一个。这种Hard Code的方式实在不讨我喜。")
    slt.markdown("&ensp;&ensp;&ensp;&ensp;下面是一段加密后呈现乱码的表情包文件的实例：")
    with open("./static/files/51b609ce8f40f68bcb387dbf96d74059", "rb") as file:
        btn = slt.download_button(
            label="点击下载乱码",
            data=file,
            file_name="51b609ce",
        )
    slt.markdown("-------------")
    slt.markdown("### 统计")
    Rank1 = Image.open("./static/pics/嗷呜rank1.png")
    Rank2 = Image.open("./static/pics/嘿嘿rank3.png")
    Rank3 = Image.open("./static/pics/嘿嘿rank8.png")
    Rank4 = Image.open("./static/pics/嘿嘿rank10.png")
    # Rank5 = Image.open("./static/pics/动画表情rank8.png")
    # Rank6 = Image.open("./static/pics/嘿嘿rank9.png")
    # Rank7 = Image.open("./static/pics/害羞rank10.png")

    slt.markdown("&ensp;&ensp;&ensp;&ensp;现在我们从表情包使用数量着手。下图展示了使用次数最多的10张表情：")

    slt.image([Rank1, Rank2, Rank3, Rank4], width=150)

    file_1 = open("./static/pics/开心rank2.gif", "rb")
    contents = file_1.read()
    data_url_1 = base64.b64encode(contents).decode("utf-8")
    file_1.close()

    file_2 = open("./static/pics/按摩rank4.gif", "rb")
    contents = file_2.read()
    data_url_2 = base64.b64encode(contents).decode("utf-8")
    file_2.close()

    file_3 = open("./static/pics/嘿嘿rank5.gif", "rb")
    contents = file_3.read()
    data_url_3 = base64.b64encode(contents).decode("utf-8")
    file_3.close()

    file_4 = open("./static/pics/嘿嘿rank6.gif", "rb")
    contents = file_4.read()
    data_url_4 = base64.b64encode(contents).decode("utf-8")
    file_4.close()

    file_5 = open("./static/pics/嘿嘿rank7.gif", "rb")
    contents = file_5.read()
    data_url_5 = base64.b64encode(contents).decode("utf-8")
    file_5.close()

    file_6 = open("./static/pics/打你rank9.gif", "rb")
    contents = file_6.read()
    data_url_6 = base64.b64encode(contents).decode("utf-8")
    file_6.close()

    # file_7 = open("./static/pics/嘿嘿rank10.gif", "rb")
    # contents = file_7.read()
    # data_url_7 = base64.b64encode(contents).decode("utf-8")
    # file_7.close()

    slt.markdown(f'<img src="data:image/gif;base64,{data_url_1}" alt="cat gif">\
        <img src="data:image/gif;base64,{data_url_2}" alt="cat gif"> \
         <img src="data:image/gif;base64,{data_url_3}" alt="cat gif"> \
            <img src="data:image/gif;base64,{data_url_4}" alt="cat gif"> \
            <img src="data:image/gif;base64,{data_url_5}" alt="cat gif"> \
            <img src="data:image/gif;base64,{data_url_6}" alt="cat gif">',
                 unsafe_allow_html=True)
    slt.markdown("两行依次是：")
    slt.markdown(
        f"- [嗷呜] ({emoji_type[0][1]}次，1/10)、[嘿嘿] ({emoji_type[2][1]}次，3/10)、 [嘿嘿] ({emoji_type[7][1]}次，8/10)、[嘿嘿] ({emoji_type[9][1]}次，10/10)")
    slt.markdown(
        f"- [开心] ({emoji_type[1][1]}次，2/10)、 [按摩] ({emoji_type[3][1]}次，4/10)、 [嘿嘿] ({emoji_type[4][1]}次，5/10)、[嘿嘿] ({emoji_type[5][1]}次，6/10)、[嘿嘿] ({emoji_type[6][1]}次，7/10)、[打你] ({emoji_type[8][1]}次，9/10)")

    slt.markdown("""
    -----------

    &ensp;&ensp;&ensp;&ensp;这里有几个非常好玩的细节。首先，我们使用次数最多的表情包依然是那个绿色的小青蛙。上一个版本的表情包统计中，它就因为使用次数最多位居榜首。没想到一年之后，它依然是使用次数最多的那个。（我们当初是有多闲才会一直发这个表情啊哈哈哈哈）

    &ensp;&ensp;&ensp;&ensp;其次，10个最常使用的表情里，光是“嘿嘿”就占了6个，共计1239次。如果问我们最想用表情包表达的一句话，那么一定非“嘿嘿”莫属。

    > &ensp;&ensp;&ensp;&ensp;而且..似乎每个含有“嘿嘿”的表情包都会被我们玩坏玩腻，从小青蛙到小绵羊到小狗。

    &ensp;&ensp;&ensp;&ensp;最后，前一版的表情分析器中，前6个常用表情只有一个是GIF动图，而这次的常用表情中，前6个有4个GIF动图。相比于刚刚相遇时的羞涩，我们似乎更喜欢用一些可爱且会动的小表情。

    > &ensp;&ensp;&ensp;&ensp; P.S. 那个出现了179次的“打你”异常瞩目～    
    """)
    y_ipt = [EMOJI_INCREMENT[i] for i in EVERY_DAY]
    for i in range(1, len(y_ipt)):
        y_ipt[i] += y_ipt[i - 1]
    bar3 = (
        Line(init_opts=opts.InitOpts())
        .add_xaxis(xaxis_data=list(EVERY_DAY))
        .add_yaxis(
            series_name="使用的总Emoji数量累积图", y_axis=y_ipt,  is_step=True
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(
                # type_="value",
                # axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
    )

    tl = Timeline()
    for num in range(10):
        EMOJI_TOP_TEN_CNT = [EMOJI_TOP_TEN[num][i] for i in EVERY_DAY]
        for l in range(1, len(EMOJI_TOP_TEN_CNT)):
            EMOJI_TOP_TEN_CNT[l] += EMOJI_TOP_TEN_CNT[l - 1]
        barten = (
            Bar()
            .add_xaxis(EVERY_DAY)
            .add_yaxis(
                "总使用次数",
                EMOJI_TOP_TEN_CNT,
                category_gap=0,
                label_opts=opts.LabelOpts(is_show=False),
                stack="Stack1"
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"使用量累积图"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                # TODO: 需要在更新代码的时候补充
                # graphic_opts=[
                #     opts.GraphicImage(
                #         graphic_item=opts.GraphicItem(
                #             id_="logo", left=20, top=20, z=-10, bounding="raw", origin=[75, 75]
                #         ),
                #         graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                #             image="static/pics/嘿嘿rank3.png",
                #             width=150,
                #             height=150,
                #             opacity=0.4,
                #         ),
                #     )
                # ],
            )
        )
        tl.add(barten, "Rank_{}".format(num))

    st_pyecharts(tl, height="350px")

    slt.info(
        "&ensp;&ensp;&ensp;&ensp;上面这个图你可以视作数量累积函数，如果图形陡峭，说明在那个周期内这个表情使用次数很多，反之，表明使用较少，长期不增长；点击下方进度条左侧的开始按钮，可以观看时间轴～")
    slt.write("这张图还有个很有意思的点，在于你可以Get到每一个表情的“时效性”，它什么时候最先开始使用、什么时候使用得少了。比如使用量位于第一的“嗷呜”，2021年11月12日就已经被我们使用了，但从2022年8月5日后，它就再也没有出现在我们的聊天记录中。")
    slt.write(
        "&ensp;&ensp;&ensp;&ensp;比如使用量第二的“开心”，那个走着六亲不认步伐的小兔子，去年7月9日第一次被使用，在2个半月（到9月23日）中接连使用了263次后，便几乎不再出现；")
    slt.write(
        "&ensp;&ensp;&ensp;&ensp;形成鲜明对比的是排名靠后但处于上升趋势的线条小狗们。他们的使用时间不长，排名第五的“嘿嘿”出现得最晚，直到今年1月12号才第一次出现在记录中，并且依然有上升的潜力。")
    st_pyecharts(bar3)

    slt.write(
        "&ensp;&ensp;&ensp;&ensp;上面这个折线图展现的是我们使用新的表情的数量。我原本以为会是一个陡峭不均的折线，实际上，\
            我们以一个相对均匀的速度，使用新的表情包（当然也意味着旧的表情包不再使用）截止到数据统计日，我们使用了1343个不同的表情。有时候回看微信自己发的和收藏的各种表情，看着自己曾经使用但是现在几乎从来不会点开的表情包，那是埋藏在记忆和数据里的宝藏吧。")
    result_lbtest = lb_test(list(INPUT_DF["EMOJIS"]), lags=20)  # 使用的博主自己的数据
    # tmp_top_10 = emoticon_creaters.most_common(10)
    slt.markdown("""
    ----

    ### 表情包分析

    > &ensp;&ensp;&ensp;&ensp;上面分析的都是单个具体的表情的使用情况，如果我们从更加宏观的角度来看，把每个表情归纳到它所属的表情包中，会发现什么有意思的结论呢？

    > &ensp;&ensp;&ensp;&ensp;下图笑笑借助微信提供的表情包数据，逆向获取了其中80%的表情所属的表情包（不可能是100%因为有很多表情是自定义表情，并不会有所属于的表情包），并把最常用的10个表情包罗列在了下面。（从左到右从上到下分别为1～10名）。
    """)
    display_most_used_authors()

    slt.markdown("""
    > &ensp;&ensp;&ensp;&ensp;我宣布我们用过的最多的表情包是～～软！萌！兔！这个表情包里的表情，我们用过了1200+次！
    > 
    > &ensp;&ensp;&ensp;&ensp;永远的线条小狗，除开刚出不久的第5套表情包外，4套表情包全部上榜了！还有谁能拒绝可爱的小狗呢！！还有谁！！（抱着小狗亲）（派小狗给瑜瑜道晚安）
    > 
    > &ensp;&ensp;&ensp;&ensp;阿八和小眠羊！可爱的表情包！虽然只出了两款，但是真的很可爱！
    """)
    # slt.write(result_lbtest)
    # print(result_lbtest['lb_pvalue'][1])


emoji_type_analysis()


slt.markdown("""
----------------
## 表情包的时序分析

""")


def TimeSeries_analysis():
    # ============ 先做一个Ljuner - Box 检验 看看是不是白噪声 ===========
    result_lbtest = lb_test(list(INPUT_DF["EMOJIS"]), lags=20)  # 使用的博主自己的数据
    # slt.write(result_lbtest)
    slt.markdown(
        "&ensp;&ensp;&ensp;&ensp;这一块使用了一些传统时间序列的检验方法。首先借助[Ljung-Box检验](https://www.math.pku.edu.cn/teachers/lidf/course/atsa/atsanotes/html/_atsanotes/atsa-wntest.html)检查时间序列本身是否为白噪声。")
    slt.markdown("&ensp;&ensp;&ensp;&ensp;最终检测结果P-value = " +
                 str(result_lbtest['lb_pvalue'][1]) + ". 拒绝原假设，说明在表情包的每天使用次数并不是一个白噪声序列。")
    # slt.write(result_lbtest)
    slt.caption(
        "&ensp;&ensp;&ensp;&ensp;要是是白噪声，那这每天发送的表情包都挺没有意义的（毕竟是“噪声”嘛）。这个检验至少证明了那些絮絮叨叨的表情包并不是无意义的噪声：他们不随机出现，却总能扮演一些重要角色。🦁")
    # slt.write(adf(list(INPUT_DF["EMOJIS"].diff(1).dropna())))

    pyplot_col1, pyplot_col2 = slt.columns(2)

    ts_fig2, ax = plt.subplots()
    ts_fig2 = plot_acf(INPUT_DF["EMOJIS"], lags=20)

    df_result = adf(INPUT_DF["EMOJIS"].diff(1).dropna())
    pyplot_col1.write("\n")
    pyplot_col1.write("&ensp;&ensp;&ensp;&ensp;虽然检验证明了它不是一个白噪声，但是它依然有可能存在自相关性，是一个漂移的随机游走过程。所以笑笑又对时序数据的一阶差分做了一个[增广Dicky Fuller检验（ADF）](https://developer.aliyun.com/article/924501)。用来判断\
                      是否为一个随机游走的序列，同时检验其平稳性。")
    pyplot_col1.write(
        "&ensp;&ensp;&ensp;&ensp;检验结果显示，在 < 1%的置信区间内，[一阶差分](https://baike.baidu.com/item/差分法)后的日表情包使用量是一个平稳的序列，这也就说明原表情包使用量是一个**随机游走过程**。")
    pyplot_col1.caption("难以置信，这个小项目还做出了学术结论（x")
    pyplot_col1.write(
        f"ADF Statistic: {df_result[0]};\n")
    pyplot_col1.write(f"p-value: {df_result[1]}")
    # pyplot_col1.write(f"p-value: {df_result[1]}")
    # pyplot_col1.write("Critical Values:")

    for key, value in df_result[4].items():

        # print(key)
        pyplot_col1.caption("%s: %.3f" % (key, value))
    pyplot_col2.pyplot(ts_fig2)

    slt.markdown("""


    --- 

    > &ensp;&ensp;&ensp;&ensp;到这里这份聊天记录分析差不多就结束啦！又带瑜瑜子走过了一年的时间，这段时间说长不长，说短不短，但是连表情包，都能看出我们点点滴滴的习惯——可能这就是数据的魅力吧。
    > 
    > 到这里数据分析的部分就结束了，后面还有两个具体的板块，一个是笑笑最后想对瑜瑜说的话（全是私货，还有一些自我感动的结项感想），还有一个是参考链接。当然这个网站**有一部分被笑笑隐藏起来了**，这里埋一个伏笔。在将来的某一天，等它孵化成熟，瑜瑜应该会看到那个独特的它出现。
    """)


TimeSeries_analysis()
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
