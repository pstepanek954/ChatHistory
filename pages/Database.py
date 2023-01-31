# streamlit_app.py

import streamlit as st
import sqlite3

# # Initialize connection.
# # Uses st.experimental_singleton to only run once.
# @st.experimental_singleton
# def init_connection():
#     return sqlite3.connect('../chathistory.db')

CONN = sqlite3.connect('./chathistory.db')
# cur = conn.cursor()


def run_query(query):
    cur = CONN.cursor()
    result = cur.execute(query)
    for i in result.fetchall():
        st.write(i[0])
    return result.fetchall()
    

run_query("select createTime from chathistory where Message like \"嘿嘿嘿\"")



# cur.close()
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