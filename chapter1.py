import streamlit as slt
import datetime
import json
import time
import copy

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
    temp = "hshas"
    with open(address, "r", encoding = "utf8")  as f:
        temp = json.load(f)
        print("RUN")
    return temp
    
ADDRESS = "./chathistory.json"
CHAT_HISTORY = load_data(ADDRESS)
slt.write(len(CHAT_HISTORY))



    


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