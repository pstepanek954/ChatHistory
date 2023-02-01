# streamlit_app.py

import streamlit as st
import json
import sqlite3
import time
# # Initialize connection.
# # Uses st.experimental_singleton to only run once.
# @st.experimental_singleton
# def init_connection():
#     return sqlite3.connect('../chathistory.db')

CONN = sqlite3.connect('./chathistory.db')

def run_query(query_sentence):
    cur = CONN.cursor()
    
    query = f"select createTime from chathistory where Message like \"%{query_sentence}%\" "
    # print(query)
    t = cur.execute(query).fetchall()
    st.write("总共出现了：", str(len(t)), "次！")

content = st.text_input('找找这句话！', '')
if len(content) > 0:
    run_query(content)

cur_time = time.perf_counter()
cur = CONN.cursor()
t1 = "select createTime, Des, Message, Type from chathistory"
t2 = cur.execute(t1).fetchall()


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