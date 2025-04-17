import streamlit as st
import pandas as pd

st.set_page_config(page_title="CFP Tracker", layout="wide")
st.title("Call for Proposals (CFP) Tracker")

@st.cache_data
def load_data():
    return pd.read_csv("grants_database.csv")

df = load_data()
st.dataframe(df)

