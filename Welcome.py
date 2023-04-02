import streamlit as slt
import datetime


from streamlit_echarts import st_pyecharts
import os
import sqlite3
from PIL import Image


slt.set_page_config(
    page_title="奇奇怪怪的聊天中心站",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
)
os.environ['TZ'] = 'Asia/Shanghai'

slt.title("奇奇怪怪的聊天中心站！")

slt.markdown("--------------")

NOW = datetime.datetime.now()
wkDays = {
    "Monday": "星期一",
    "Tuesday": "星期二",
    "Wednesday": "星期三",
    "Thursday": "星期四",
    "Friday": "星期五",
    "Saturday": "星期六",
    "Sunday": "星期天",
}
MeetDay = "2021-10-08 21:45:08"
col1, col2, col3 = slt.columns(3)
col1.metric("今天是～", f"{NOW.strftime('%Y-%m-%d')}", "1 day~")
col2.metric("今天是个～", f"{wkDays[NOW.strftime('%A')]}", "1 day~")
col3.metric(
    "今天是和瑜瑜的～", f"第{(datetime.datetime.strptime(NOW.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.datetime.strptime(MeetDay, '%Y-%m-%d %H:%M:%S')).days}天🥰", "1 day~")


col4, col5, col6 = slt.columns(3)
col4.text("")
col5.text("""
                                        ┊┊┊☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆
                                        ┊┊┊╭┻┻┻┻┻┻┻┻┻┻┻┻┻┻┻┻┻┻┻┻╮┊┊┊
                                        ┊┊┊┃╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲┃┊┊┊
                                        ┊┊╭┻━━━━━━━━━━━━━━━━━━━━┻╮┊┊
                                        ┊┊┃╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲┃┊┊
                                        ╱▔┗━━━━━━━━━━━━━━━━━━━━━━┛▔╲

""")
col6.text("")

slt.markdown("""
------

# ✍️ 写在前面

> &ensp;&ensp;&ensp;&ensp;Hello～亲爱的天瑜！你好呀～～这里是笑笑！先祝瑜瑜20岁生日快乐！🎂！吃蛋糕！吃蛋糕！（拿起刀叉🍴）
>
> &ensp;&ensp;&ensp;&ensp;和去年一样，笑笑每个重要的节日喜欢准备两份小小的礼物🎁，一起送给瑜瑜。这里，就是第二份小礼物。瑜瑜可以像拆开一个礼品盒一样“拆开”这个网站。
>
> &ensp;&ensp;&ensp;&ensp;不同的是，拆开礼品盒时候内心的感受，往往是触摸到礼品盒，感受到“礼物就在里面”的蠢蠢欲动带来的。那么当一个礼物你摸不到，只能用自己的双眼去观看的时候，它本身的意义就是不同于礼品盒的。
>
> &ensp;&ensp;&ensp;&ensp;瑜瑜如果还记得，前两周有次瑜瑜给笑笑发小红书的，那个衡中的毕业生，写自己长大后回顾过去的文字。瑜瑜说：**感觉自己回到了风扇呜呜转的逼仄教室。**
>
> &ensp;&ensp;&ensp;&ensp;笑笑当时说，感觉作者在**仔细地检视我的青春**。
>
> &ensp;&ensp;&ensp;&ensp;那么，这份礼物，就是在仔细检视我们过去的一年半载，把折叠的记忆摊平到网页上，然后告诉自己：原来，我又长大了一岁。原来，我已经走过了这么多路。
>
> &ensp;&ensp;&ensp;&ensp;笑笑能参与到这个过程中，是我的荣幸。我和世间无数人一样，只是在帮助见证这一切的发生。
>
> &ensp;&ensp;&ensp;&ensp;现在，按照目录顺序，开始吧。

-------

""")


slt.markdown("""
# 🎁 关于这个礼物

> &ensp;&ensp;&ensp;&ensp;去年笑笑给瑜瑜自制了一个小网站，如果在互联网森林里迷路了，[这里是传送门](https://comforting-entremet-a54957.netlify.app/index.html)。里面笑笑梳理了我们相识到恋爱的半年多时间里的8万多条微信聊天记录，做了一点微小的工作，从数据本身出发做了一些简单的分析。发现这件事情是完全可行并且颇有意义的。不过当时的网站是个相当粗制滥造的产品。从概念产生到制作完成总共花费了12天的时间。而今年，笑笑把去年的网站做了一个全面的更新。
>
> &ensp;&ensp;&ensp;&ensp;笑笑搜集了截至2023年3月27日我们之间的所有微信聊天记录，一共23万多条，并存储在了一个数据库中，借助一个很好上手的Python网页制作框架Streamlit搭建了一个聊天记录分析网站2.0，并把它部署在了Streamlit的云服务器上。
>
> &ensp;&ensp;&ensp;&ensp;这个网站的整体UI/UX都在初代版本上有了较好的迭代和更新，主要更新方向有：
>
> - **用户友好，增强用户反馈性、交互性**：笑笑添加了一部分交互界面，给瑜瑜提供了一定的操纵性（比如查询功能），并且对接了后台数据库（充分安全🔐地）；
>
> - **提高了系统可复用性**：初代版本是完全静态页面，而这个网站90%的分析是完全基于数据库的。这意味着如果我希望这个系统“更新状态至某年月日”，我只需要更新后台的数据库——而不需要重写所有的代码、算法、分析流程；同样的，这也意味着如果我想要加上什么新的功能，我可以就在目前版本的基础上进行修改、完善，而不需要动辄推倒重来。
>
> - **引入了更加强大的自然语言分析（NLP）技术**：去年的自然语言分析部分比较粗浅，甚至连LSTM都没有用上，今年的自然语言分析模块引入了transformers / Attention + 神经网络机制，能够对语句情感做出更加综合、全面、细致的分析。
>
> - **完善了代码保存与更新机制、对相应界面做了展示**；
>
> - **修改了项目手册与参考外链**；

""")

slt.markdown("""

------------
# 🔍 可能出现的Bug和应对方案

> &ensp;&ensp;&ensp;&ensp;因为网站所有的数据是实时采集、构建、展示的，所以，你可以想象在你阅读后面板块的文字的时候，遥远的海外一台服务器上正在飞速进行着23w条数据、约100MB大小数据的分析。也正因此，必须采用一些缓存优化的技术进行权衡取舍，减少运行损耗。
> 
> &ensp;&ensp;&ensp;&ensp;系统默认在加载A-Abstract（也就是第二个页面时）进行所有数据的缓存与处理，因此如果出现Bug，请先点击目录中的A-Abstract界面，浏览完毕后再点击其他界面。它会自动重新刷新并reload数据。这是最高效地解决Bug的方法。
> 
> &ensp;&ensp;&ensp;&ensp;例如，有可能打开一些页面出现如下图所示的Bug，按照上述操作执行即可。
> 
> &ensp;&ensp;&ensp;&ensp;为了减少这种情况的发生，建议浏览网站时按照左侧目录栏的顺序依次浏览，特此说明。

""")

colA, colB = slt.columns(2)
failure = Image.open("./static/pics/failure.png")
colA.image(failure)
colA.caption("🤦好吧这张图不管怎么搞，放在这里看起来确实就像这个页面出Bug了，但是如果你能看到这张图就说明它其实没有😄。")
