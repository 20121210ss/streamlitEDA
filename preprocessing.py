import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import allVariable

def preprocessing():
    col1, col2 = st.columns(spec=[0.7,0.3])
    with col1:
        st.tabs(['資料集'])
        st.data_editor(allVariable.df)
    with col2:
        st.tabs(['前處理動作'])
        if st.button("刪除遺漏值"):
            st.warning("ok")
    
if allVariable.df is not None:
    preprocessing()
else:
    st.error("請匯入資料集")
    