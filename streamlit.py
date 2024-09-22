import streamlit as st

#set the app title 
st.title("My First Streamlit App")

#this is how you "writing"
st.write("Welcome to my Streamlit app!")

#adding the button
st.button("Reset",  type = "primary")
if st.button("Say Hello"):
    st.write("Why hello there!")
    st.balloons()
    st.image("spacecat.png", caption="Cat  in space", width=200)

else:
    st.write("Goodbye!")
