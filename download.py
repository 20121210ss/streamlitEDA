import streamlit as st
st.set_page_config(page_title="EDA App",layout="wide")

import allVariable
from main import getDataframe

df = None

def download():
    
    df = getDataframe()
    
    # 大標
    st.subheader("匯出🗳️")
    
    # 整個頁面拆成5:5的分布   
    col1, col2 = st.columns(spec=[0.6,0.5])
    
    with col1:
        st.tabs(['目前資料集'])
        showData = st.empty()
        showData.data_editor(df)
        # 提供下載資料的按鈕
        st.download_button(label="Download data as CSV", data=convert_df(df), file_name='edited_df.csv', mime='text/csv')
    
    with col2:
        st.tabs(['目前code彙整'])
        code_placeholder = st.empty()    
        code_placeholder.code(allVariable.outputCode, language="python", line_numbers=True)
        st.download_button(label="Download code as Python", data=allVariable.outputCode, file_name='edited_df_code.py')
   
         
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
        
if allVariable.df is not None:
    df = getDataframe()
    download()
else:
    st.error("請匯入資料集")

    
    
    