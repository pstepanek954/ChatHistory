import json

import sqlite3


conn = sqlite3.connect('chathistory.db')
cur = conn.cursor()
 
cur.execute('CREATE TABLE CHATHISTORY(CreateTime Integer DEFAULT 0, Des INTEGER, ImgStatus INTEGER DEFAULT 0, MesLocalID INTEGER PRIMARY KEY , Message LONGTEXT, MesSvrID BIGINT DEFAULT 0, Status INTEGER DEFAULT 0, TableVer INTEGER DEFAULT 1, Type INTEGER);')
conn.commit()

with open("./chathistory.json", "r", encoding = "utf8")  as f:
    temp = json.load(f) # 加载数据
    idx = 0
    for i in temp:
        effect =cur.execute(
            "insert into chathistory(CreateTime, Des , ImgStatus , MesLocalID  , Message, MesSvrID , Status , TableVer , Type) values (?,?,?,?,?,?,?,?,?)"
            ,(i["CreateTime"], i["Des"],i["ImgStatus"],i["MesLocalID"],
              i["Message"], i["MesSvrID"], i["Status"],i["TableVer"], i["Type"]))
        conn.commit()
        idx += 1
        print(idx)
cur.close()
conn.close()
