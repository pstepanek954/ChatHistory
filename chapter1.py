import streamlit as slt
import datetime


@slt.cache
def show_100():
    return range(100)

def run():
    slt.title("Tutorials Streamlit")

    slt.info("Hello fellow!")

    slt.header("Header")

    slt.subheader("SubHeader")

    slt.success("Success")

    slt.warning("Warning")

    slt.markdown("$$  f(x) = x$$")

    slt.write("Write here.")

    
    # img = Image.open("picx1.png")

    # slt.image(img, width= 300, caption="picx1")

    if slt.checkbox("Hide/Show"):
        slt.text("Clicked")

    occupation = slt.selectbox("Your occupation", ["Ds", "farmer", "Teacher"])
    slt.write(occupation)

    location = slt.multiselect("Where do you work?", ["Beijing", "Shanghai", "Chengdu"])

    slt.write("You select " , len(location), " Locations")

    level = slt.slider("Whats your level?", 2,100)

    first_name = slt.text_input("Your first name?", "Type here..") 
    result = ""
    if slt.button("Submit"):
        result = first_name.title()
        slt.success(result)


    today = slt.date_input("Today is ", datetime.datetime.now())

    time_ = slt.time_input("Time is ", datetime.time())

    slt.json({"Name" : result, "Age" : level})

    my_bar = slt.progress(0)
    for p in range(10):
        my_bar.progress(p + 1)

    # slt.balloons()
# sudo rm -rf /Library/Developer/CommandLineTools
#   sudo xcode-select --install
    slt.sidebar.header("About")


    slt.sidebar.write(show_100())

if __name__ == "__main__":
    run()