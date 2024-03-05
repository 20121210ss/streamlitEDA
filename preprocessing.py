import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import allVariable

def preprocessing():
    st.tabs(['資料集前處理'])
    
if allVariable.df is not None:
    preprocessing()
else:
    st.error("請匯入資料集")
    