from collections import defaultdict


a = defaultdict(int)


t = "<msg><emoji md5=\"b55191db0f3398491c9fbd09ff7472c0\" type=\"2\" len = \"97494\" productid=\"com.tencent.xin.emoticon.person.stiker_1578974601f2b6d377c0f2575f\" width=\"240\" height=\"240\"></emoji><gameext type=\"0\" content=\"0\" ></gameext></msg>"

loca = t.find('productid=\"com.tencent.xin.emoticon.person.stiker')
a[t[loca + 50 : loca + 76]] += 1
print(a)
# print(len('productid=\"com.tencent.xin.emoticon.person.stiker'))