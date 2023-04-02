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

    t = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", t.timetuple())[:10]
    return otherStyleTime


def timestamp_2_date(n):
    return get_local_time_ten(n[0])


os.environ['TZ'] = 'Asia/Shanghai'

total_txt = pd.read_csv("./static/files/All_data.csv")
CONN = sqlite3.connect('./static/files/20230327.db')

EVERY_DAY = st.session_state.every_day


def run_query(query_sentence):
    cur = CONN.cursor()
    query_girl = f"select createTime, Des from chathistory where Message like \"%{query_sentence}%\" and Des = 1 and Type = 1"
    query_boy = f"select createTime, Des from chathistory where Message like \"%{query_sentence}%\" and Des = 0 and Type = 1"
    t1 = cur.execute(query_girl).fetchall()
    t2 = cur.execute(query_boy).fetchall()

    st.write(f"瑜瑜子说了{query_sentence}：{len(t1)} 次，笑笑说了{len(t2)}次。")

    res_girl = list(map(timestamp_2_date, t1))
    res_boy = list(map(timestamp_2_date, t2))
    cnt_mac_girl = Counter(res_girl)
    cnt_mac_boy = Counter(res_boy)
    y_axis_girl = []
    y_axis_boy = []
    for idx, i in enumerate(EVERY_DAY):
        y_axis_girl.append(cnt_mac_girl[i])
        y_axis_boy.append(cnt_mac_boy[i])
        if idx > 0:
            y_axis_girl[-1] += y_axis_girl[-2]
            y_axis_boy[-1] += y_axis_boy[-2]

    c = (
        Bar()
        .add_xaxis(EVERY_DAY)
        .add_yaxis(
            "瑜瑜子的！",
            y_axis_girl,
            category_gap=0,
            label_opts=opts.LabelOpts(is_show=False),
            stack="Stack1"
        )
        .add_yaxis(
            "笑笑子的！",
            y_axis_boy,
            category_gap=0,
            label_opts=opts.LabelOpts(is_show=False),
            stack="Stack1"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"那些说'{query_sentence}'的日子"),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
    )

    st_pyecharts(c, height="350px")
    st.caption("💡这里的数量是累积数量，$y_t$也就是第1天到第$t$天消息的总和～")


def contents_abst():
    # 看一下大致的NLP的情况
    contents = st.session_state.talks_contents
    st.markdown("### 字符长度\n ------")
    st.markdown(
        f"- 这一部分是纯粹的NLP分析。在此之前去除了所有的表情包、图片以及系统提示，最终获得了{len(contents)}条纯文本文字。这是占比\
            最多的一部分。首先是对每条信息的长度进行分析。下图展示的是文本对话的长度分布。\n - 有点像t-分布是怎么回事...哈哈哈哈哈 \
                 哈 \n - 大多数文本都在10个字符以内结束了，但是依然不乏长长的絮叨（或者是吐槽或者是发疯！一起疯狂！），总体来说是一个**长长长尾分布**。")
    st.caption("这里其实有一个小问题。微信自带表情比如[开心]在这里就会占用4个字符长度，会对长度统计造成一定的失真。")
    t = Counter([len(cnt[0]) for cnt in contents])

    word_len_res = dict()
    word_len_res[">30"] = 0
    for i in t:
        if i <= 30:
            word_len_res[i] = t[i]
        else:
            word_len_res[">30"] += t[i]
    # print(res)
    # st.write(word_len_res) # 展示每个字符被使用了多少次
    X_axis = [i for i in range(1, 30)]
    X_axis.append(">30")
    barten = (
        Bar()
        .add_xaxis(X_axis)
        .add_yaxis(
            "出现次数",
            [word_len_res[i] for i in X_axis],
            category_gap=0,
            label_opts=opts.LabelOpts(is_show=False),
            stack="Stack1"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="文字长度分布"),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
    )
    st_pyecharts(barten, height="350px")
    st.markdown("- 我们之间单次发送的最长消息，含有2048个字符。最开始出现这个结果的时候我是不敢相信的，当把这条消息定位出来之后，发现它距离现在如此的近：在今年3月11日22点11分，瑜瑜子发送了这条长达2048个字符长度的文本，我们一起来欣赏一下～")
    for i in contents:
        if len(i[0]) == 2048:
            st.markdown('```Python ' + i[0] + ' \n```')
    st.markdown("- 这！为什么如此眼熟！这是我们的软工作业！画笔画画Turtle那个！")
    st.markdown(
        "P.S. 至于这里看起来似乎没有2048个字符，一个可能的解释是从Vscode把它复制下来的时候微信自动添加了空格补全或者 \"\\t\"等符号，一下子把它变得很长了！")


def Emotion_Reflect():
    """_summary_
    可视化情绪指标
    """
    st.markdown("### 文本情感分析 \n -------")

    st.markdown(
        """
        > 这一部分是整个聊天记录分析器中难度最高的部分（也是技术需求最高和耗时最久的部分）。初代版本是完全没有考虑从文本情感含义的角度进行分析的，这次，笑笑没有让它成为遗憾。
        > 
        > 总的来说，根据现有中文文本，人们已经可以较为准确地拿捏每一句话的情感倾向并进行打分。利用公开数据集+Transformer/Attention机制进行分析已经成为行业标杆般的技术路线。由于实在太火，找到现成Demo也就不那么困难。
        > 
        > 难点在于跑完所有的20w条数据。由于时间有限，即使有了现成的Bert模型，单靠CPU完整地处理完20w+的海量文本也是个不小的任务。最终借助了一些Python小工具，笑笑成功地把任务压缩分割在了一天之内。
        > 
        > 出于计算简单考虑，每条消息只有“积极/消极/中性”三种情况。我们把三种情绪在每天聊天中的占比分别计算出来，拉伸到整个时间区间，最终绘制出了下面这张图。这里，有我们所有的情绪。
        """)
    all_time = list(total_txt["CreateTime"])
    all_emotions = list(total_txt["Emotions"])
    all_day_emo = dict()
    for day in EVERY_DAY:
        all_day_emo[day] = [0, 0, 0]
    for idx, tmp_time in enumerate(all_time):
        cur_date = get_local_time_ten(tmp_time)
        if all_emotions[idx] == "积极":
            all_day_emo[cur_date][0] += 1
        elif all_emotions[idx] == "中性":
            all_day_emo[cur_date][1] += 1
        else:
            all_day_emo[cur_date][2] += 1
    for i in all_day_emo:
        agin = sum(all_day_emo[i])
        if agin == 0:
            agin += 1

        all_day_emo[i].append(agin)

    lastOne = (
        Bar()
        .add_xaxis(EVERY_DAY)
        .add_yaxis(
            "积极",
            [all_day_emo[i][0]/(all_day_emo[i][3]+1) for i in EVERY_DAY],
            category_gap=0,
            label_opts=opts.LabelOpts(is_show=False),
            stack="Stack1"
        )
        .add_yaxis(
            "中性",
            [all_day_emo[i][1]/(all_day_emo[i][3]+1) for i in EVERY_DAY],
            category_gap=0,
            label_opts=opts.LabelOpts(is_show=False),
            stack="Stack1"
        )
        .add_yaxis(
            "消极",
            [all_day_emo[i][2]/(all_day_emo[i][3]+1) for i in EVERY_DAY],
            category_gap=0,
            label_opts=opts.LabelOpts(is_show=False),
            stack="Stack1"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="情绪分析器"),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
    )

    st_pyecharts(lastOne, height="350px")
    st.markdown(
        """
        > 普遍来说，中性情绪占比更多一些，毕竟很多微信的沟通都只是简单的絮絮叨叨。如果排除这些日常琐碎，你会看到一个积极、乐观的我们。否则，我们不会走到今天，兜兜转转又是一年。
        > 
        > 不管是假期、学习还是考试周，还有什么会比一颗时时积极面对生活的心更能对抗生活的纷纷扰扰呢？
        > 
        > 汪汪队立大功！积极瑜瑜！不怕困难！
        > 
        > 你是最棒的！我也是！我们都是最棒的自己！
        """)
    st.markdown("""
    --------
    ### 结语
    

    > 针对NLP的数据分析到这里基本就结束啦。最后一部分是关于表情包的分析。这一部分NLP看起来有些虎头蛇尾，因为对于这占比近90%的文本，似乎分析还不够深入。这主要是由于：
    - 一开始处理微信自带表情嵌入在文本中，较难删除，并且我有段时间是英文版微信，所以正则提取十分困难；这个卡脖子问题还影响到了后续的表情包分析的模块；此处按下不表；
    - 20w条数据的情绪分析时间较长，所以到了项目末期几乎抽不出手来做进一步的NLP分析（比如词云图、用词习惯等）。这一部分后续有很大的发展潜力；
    - 懒惰（删掉）。

                 """)


st.title("自然语言分析")
st.markdown("------")


st.markdown("### 一个小玩具")
content = st.text_input('🧸 这是一个聊天记录检索器，找找这句话！', '')
st.caption("支持Emoji查询，可以模糊匹配。非常有意思。可以试着输入：")
st.markdown("> 瑜瑜子 / 🥺 / 早 / 哈哈哈 / 晚安 / 👀 / ...")
if len(content) > 0:
    run_query(content)


contents_abst()

Emotion_Reflect()
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

# st.write("Database  Test")


# 初代：
#   66ff555af0033ee332d3b5540914d71b', 301) ✅

# ('cbd8610ac858597def3e401a848a94e2', 263) ✅

# ('4a06eb2177884ec05edc43ef2f721219', 226) ✅

# ('41d2f01c7eb7451aee7f8987bcdab700', 225) ✅

# ('1c610badc0e4ff27ecdaa0b802f4f241', 228) ❌

# ('a9fba580a23fb794760adea045fa27eb', 217) ❌

# ('cd4dc33d96b030063554e22cd02670a6', 194) ❌

# ('2f3936cbc409df79a7f040f73fd192e4', 186) ❌

# (('e2232dc6e973a21e8243050e6a58f980', 180)❌

# ('edb6978d023a7c11a9d54f294eafcc50', 179) ❌
