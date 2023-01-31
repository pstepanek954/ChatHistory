import json
import pymysql

coon=pymysql.connect(host="localhost",port=3306,user="root",password="root",db="chat")
cursor=coon.cursor()

with open("./chathistory.json", "r", encoding = "utf8")  as f:
    temp = json.load(f) # 加载数据
    idx = 0
    for i in temp:
        effect =cursor.execute(
            "insert into CHATHISTORY(CreateTime, Des , ImgStatus , MesLocalID  , Message, MesSvrID , Status , TableVer , Type) values (%r,%r,%r,%r,%r,%r,%r,%r,%r)"
            ,(i["CreateTime"], i["Des"],i["ImgStatus"],i["MesLocalID"],
              i["Message"], i["MesSvrID"], i["Status"],i["TableVer"], i["Type"]))
        coon.commit()
        idx += 1
        print(idx)
cursor.close()
coon.close()